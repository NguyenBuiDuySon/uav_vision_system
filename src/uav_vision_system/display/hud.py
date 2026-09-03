import cv2
import numpy as np

from uav_vision_system.outputs.landing_result import LandingResult


def draw_landing_hud(frame: np.ndarray, result: LandingResult) -> None:
    height, width = frame.shape[:2]

    camera_center = result.debug.get(
        "camera_center",
        np.array([width / 2.0, height / 2.0], dtype=np.float32),
    )

    _draw_camera_reference(frame, camera_center)

    if not result.detected:
        _put_text(frame, "TARGET LOST", (20, 35), (0, 0, 255), 0.8, 2)

        lost_message = (
            result.message
            if result.message != "TARGET LOST"
            else "Waiting for valid Tag16h5..."
        )

        _put_text(frame, lost_message, (20, 70), (0, 0, 255), 0.65, 2)

        detections_count = result.debug.get("detections_count")
        if detections_count is not None:
            _put_text(
                frame,
                f"RAW DETECTIONS: {detections_count}",
                (20, 105),
                (0, 0, 255),
                0.55,
                2,
            )
        return

    corners = result.debug["corners"]
    tag_center = result.debug["tag_center"]
    pad_center = result.debug["pad_center"]
    tag_forward_unit = result.debug["tag_forward_unit"]

    _draw_tag(frame, corners)
    _draw_point(frame, tag_center, "TAG CENTER", (0, 255, 255))
    _draw_point(frame, pad_center, "PAD CENTER", (0, 0, 255))

    cv2.arrowedLine(
        frame,
        _to_point(camera_center),
        _to_point(pad_center),
        (0, 255, 255),
        2,
        tipLength=0.2,
    )

    tag_front_end = tag_center + tag_forward_unit * 90.0
    cv2.arrowedLine(
        frame,
        _to_point(tag_center),
        _to_point(tag_front_end),
        (0, 128, 255),
        3,
        tipLength=0.25,
    )

    _put_text(
        frame,
        "PAD FRONT / N",
        _to_point(tag_front_end + np.array([8, 0])),
        (0, 128, 255),
        0.5,
        2,
    )

    _put_text(
        frame,
        f"TARGET LOCKED | Tag ID {result.tag_id} | CONF {result.confidence:.2f}",
        (20, 35),
        (0, 255, 0),
        0.72,
        2,
    )

    if result.forward_cm is not None and result.right_cm is not None:
        _put_text(
            frame,
            f"FORWARD ERROR: {result.forward_cm:+.1f} cm",
            (20, 70),
            (255, 255, 255),
            0.65,
            2,
        )
        _put_text(
            frame,
            f"RIGHT ERROR:   {result.right_cm:+.1f} cm",
            (20, 100),
            (255, 255, 255),
            0.65,
            2,
        )
    else:
        _put_text(
            frame,
            f"OFFSET X: {result.offset_x_px:+.0f} px",
            (20, 70),
            (255, 255, 255),
            0.65,
            2,
        )
        _put_text(
            frame,
            f"OFFSET Y: {result.offset_y_px:+.0f} px",
            (20, 100),
            (255, 255, 255),
            0.65,
            2,
        )

    _put_text(
        frame,
        f"YAW ERROR:     {result.yaw_deg:+.1f} deg",
        (20, 130),
        (255, 255, 255),
        0.65,
        2,
    )

    color = (0, 255, 0) if result.ready else (0, 255, 255)
    _put_text(frame, result.message, (20, 165), color, 0.55, 2)

    margin = result.debug.get("decision_margin", 0.0)
    hamming = result.debug.get("hamming", -1)
    area = result.debug.get("tag_area_px", 0.0)
    edge = result.debug.get("tag_edge_px", 0.0)

    _put_text(
        frame,
        f"MARGIN {margin:.1f} | HAM {hamming} | AREA {area:.0f} | EDGE {edge:.0f}px",
        (20, height - 20),
        (255, 255, 255),
        0.48,
        1,
    )


def _draw_camera_reference(frame: np.ndarray, camera_center: np.ndarray) -> None:
    center = _to_point(camera_center)

    cv2.drawMarker(
        frame,
        center,
        (255, 255, 255),
        cv2.MARKER_CROSS,
        25,
        2,
    )

    drone_front_end = np.array(
        [camera_center[0], camera_center[1] - 90],
        dtype=np.float32,
    )

    cv2.arrowedLine(
        frame,
        center,
        _to_point(drone_front_end),
        (255, 255, 255),
        2,
        tipLength=0.25,
    )

    _put_text(
        frame,
        "DRONE FRONT",
        _to_point(drone_front_end + np.array([8, 0])),
        (255, 255, 255),
        0.5,
        1,
    )


def _draw_tag(frame: np.ndarray, corners: np.ndarray) -> None:
    points = corners.astype(np.int32)
    cv2.polylines(frame, [points], True, (0, 255, 0), 2)

    for index, point in enumerate(points):
        cv2.circle(frame, _to_point(point), 4, (0, 255, 0), -1)
        _put_text(
            frame,
            str(index),
            _to_point(point + np.array([5, -5])),
            (0, 255, 0),
            0.45,
            1,
        )


def _draw_point(
    frame: np.ndarray,
    point: np.ndarray,
    label: str,
    color: tuple[int, int, int],
) -> None:
    cv2.circle(frame, _to_point(point), 6, color, -1)
    _put_text(
        frame,
        label,
        _to_point(point + np.array([8, 18])),
        color,
        0.45,
        1,
    )


def _put_text(
    frame: np.ndarray,
    text: str,
    origin: tuple[int, int],
    color: tuple[int, int, int],
    scale: float,
    thickness: int,
) -> None:
    cv2.putText(
        frame,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def _to_point(point: np.ndarray) -> tuple[int, int]:
    return int(point[0]), int(point[1])