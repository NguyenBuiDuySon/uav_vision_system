from dataclasses import dataclass, field
from typing import Any


@dataclass
class LandingResult:
    detected: bool

    offset_x_px: float = 0.0
    offset_y_px: float = 0.0

    forward_cm: float | None = None
    right_cm: float | None = None
    yaw_deg: float = 0.0

    ready: bool = False
    confidence: float = 0.0
    tag_id: int = -1
    message: str = "TARGET LOST"

    debug: dict[str, Any] = field(default_factory=dict)