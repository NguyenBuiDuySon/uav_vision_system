from dataclasses import dataclass


@dataclass(frozen=True)
class CameraConfig:
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


@dataclass(frozen=True)
class LandingTagConfig:
    tag_family: str = "tag16h5"
    target_tag_id: int = 13

    # Physical side length of the AprilTag black/white code region.
    # Current user pad tag size: 1.9 cm x 1.9 cm.
    tag_size_cm: float | None = 1.9

    # If the tag is not placed at the real pad center, measure the offset.
    # Positive forward means the tag is placed toward the pad's N direction.
    tag_offset_forward_cm: float = 4.0
    tag_offset_right_cm: float = 0.0

    # If camera looks downward and image top is drone front.
    drone_front_angle_deg: float = -90.0

    # Use this if the detected tag front does not match the pad N direction.
    # Try 0, 90, 180, -90 during calibration.
    tag_forward_yaw_offset_deg: float = 0.0

    position_deadband_px: float = 20.0
    position_deadband_cm: float = 3.0
    yaw_deadband_deg: float = 5.0

    # Keep permissive for small 1.9 cm tag.
    min_decision_margin: float = 5.0
    max_hamming: int = 2
    min_tag_area_px: float = 40.0
    lock_required_frames: int = 1


@dataclass(frozen=True)
class UartConfig:
    enabled: bool = True
    port: str = "COM6"
    baudrate: int = 115200
    send_hz: int = 10


@dataclass(frozen=True)
class AppConfig:
    camera: CameraConfig = CameraConfig()
    landing_tag: LandingTagConfig = LandingTagConfig()
    uart: UartConfig = UartConfig()
