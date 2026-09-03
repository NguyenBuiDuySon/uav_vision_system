from uav_vision_system.outputs.landing_result import LandingResult


def build_landing_packet(result: LandingResult) -> str:
    forward_cm = result.forward_cm if result.forward_cm is not None else 0.0
    right_cm = result.right_cm if result.right_cm is not None else 0.0

    payload = (
        f"LAND,"
        f"{int(result.detected)},"
        f"{forward_cm:.2f},"
        f"{right_cm:.2f},"
        f"{result.yaw_deg:.2f},"
        f"{int(result.ready)},"
        f"{result.confidence:.2f},"
        f"{result.tag_id}"
    )

    checksum = _xor_checksum(payload)
    return f"${payload}*{checksum:02X}\n"


def _xor_checksum(payload: str) -> int:
    value = 0
    for char in payload:
        value ^= ord(char)
    return value
