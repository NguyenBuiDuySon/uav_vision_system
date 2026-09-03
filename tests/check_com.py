import sys
import serial
from serial.tools import list_ports


def list_available_ports() -> None:
    print("Available ports:")
    for port in list_ports.comports():
        print(f"  {port.device} - {port.description}")


def check_port(port_name: str, baudrate: int = 115200) -> None:
    try:
        ser = serial.Serial(port_name, baudrate=baudrate, timeout=1)
        ser.close()
        print(f"{port_name}: FREE / open được")
    except serial.SerialException as exc:
        print(f"{port_name}: BUSY hoặc không mở được")
        print(f"Reason: {exc}")


if __name__ == "__main__":
    list_available_ports()

    if len(sys.argv) >= 2:
        check_port(sys.argv[1])
    else:
        print("\nUsage:")
        print("  uv run python tools/check_com.py COM4")