import serial

from uav_vision_system.communication.packet import build_landing_packet
from uav_vision_system.outputs.landing_result import LandingResult


class UartSender:
    def __init__(self, port: str, baudrate: int) -> None:
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0.02,
        )

    def send(self, result: LandingResult) -> None:
        packet = build_landing_packet(result)
        self.serial.write(packet.encode("utf-8"))

    def close(self) -> None:
        if self.serial.is_open:
            self.serial.close()