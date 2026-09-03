import time

import serial


PORT = "COM6"
BAUDRATE = 115200

PACKETS = [
    "$LAND,1,12.50,-8.20,16.40,0,0.91,13*02\n",
    "$LAND,0,0.00,0.00,0.00,0,0.00,-1*53\n",
]


def main() -> None:
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        time.sleep(2)

        for packet in PACKETS:
            print(f"TX: {packet.strip()}")
            ser.write(packet.encode("utf-8"))
            ser.flush()
            time.sleep(0.5)


if __name__ == "__main__":
    main()