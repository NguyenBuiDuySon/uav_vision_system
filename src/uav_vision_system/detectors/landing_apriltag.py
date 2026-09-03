import cv2
import numpy as np
from pupil_apriltags import Detector

from uav_vision_system.config import LandingTagConfig
from uav_vision_system.geometry.angle import (
    angle_deg_from_vector,
    normalize_angle_deg,
    rotate_counter_clockwise_90,
    rotate_clockwise_90,
    unit_vector,
    vector_from_angle_deg,
)
from uav_vision_system.outputs.landing_result import LandingResult


class LandingAprilTagDetector:
    def __init__(self, config: LandingTagConfig) -> None:
        self.config = config
        self.lock_count = 0
        self.detector = Detector(
            families=config.tag_family,
            nthreads=2,
            quad_decimate=1.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0,
        )

    def update(self, frame: np.ndarray) -> LandingResult:
        height, width = frame.shape[:2]
        camera_center = np.array([width / 2.0, height / 2.0], dtype=np.float32)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self.detector.detect(gray)

        target = self._select_target(detections)
        if target is None:
            return LandingResult(
                detected=False,
                message="TARGET LOST",
                debug={
                    "camera_center": camera_center,
                    "detections_count": len(detections),
                },
            )

        corners = target.corners.astype(np.float32)
        tag_center = target.center.astype(np.float32)
        p0, p1, p2, p3 = corners

        tag_edge_px = self._estimate_tag_edge_px(corners)
        has_tag_size = self.config.tag_size_cm is not None and self.config.tag_size_cm > 0

        cm_per_px = (
            self.config.tag_size_cm / max(tag_edge_px, 1.0)
            if has_tag_size
            else None
        )

        tag_edge_vec = unit_vector(p1 - p0)

        tag_forward_unit = rotate_counter_clockwise_90(tag_edge_vec)
        tag_forward_angle = angle_deg_from_vector(tag_forward_unit)

        tag_forward_angle = normalize_angle_deg(
            tag_forward_angle + self.config.tag_forward_yaw_offset_deg
        )

        tag_forward_unit = vector_from_angle_deg(tag_forward_angle)
        tag_right_unit = rotate_clockwise_90(tag_forward_unit)

        if cm_per_px is not None:
            pad_center = (
                tag_center
                - tag_forward_unit * (self.config.tag_offset_forward_cm / cm_per_px)
                - tag_right_unit * (self.config.tag_offset_right_cm / cm_per_px)
            )
        else:
            pad_center = tag_center

        offset_px = pad_center - camera_center
        offset_x_px = float(offset_px[0])
        offset_y_px = float(offset_px[1])

        if cm_per_px is not None:
            forward_cm = -offset_y_px * cm_per_px
            right_cm = offset_x_px * cm_per_px
            position_ready = (
                abs(forward_cm) <= self.config.position_deadband_cm
                and abs(right_cm) <= self.config.position_deadband_cm
            )
        else:
            forward_cm = None
            right_cm = None
            position_ready = (
                abs(offset_x_px) <= self.config.position_deadband_px
                and abs(offset_y_px) <= self.config.position_deadband_px
            )

        yaw_deg = normalize_angle_deg(
            tag_forward_angle - self.config.drone_front_angle_deg
        )

        ready = position_ready and abs(yaw_deg) <= self.config.yaw_deadband_deg

        confidence = self._normalize_confidence(target.decision_margin)

        message = self._build_message(
            offset_x_px=offset_x_px,
            offset_y_px=offset_y_px,
            forward_cm=forward_cm,
            right_cm=right_cm,
            yaw_deg=yaw_deg,
            ready=ready,
        )

        return LandingResult(
            detected=True,
            offset_x_px=offset_x_px,
            offset_y_px=offset_y_px,
            forward_cm=forward_cm,
            right_cm=right_cm,
            yaw_deg=yaw_deg,
            ready=ready,
            confidence=confidence,
            tag_id=int(target.tag_id),
            message=message,
            debug={
                "camera_center": camera_center,
                "corners": corners,
                "tag_center": tag_center,
                "pad_center": pad_center,
                "tag_forward_unit": tag_forward_unit,
                "cm_per_px": cm_per_px,
                "tag_edge_px": tag_edge_px,
                "decision_margin": float(target.decision_margin),
                "hamming": int(target.hamming),
                "tag_area_px": self._tag_area_px(corners),
                "detections_count": len(detections),
            },
        )

    def _select_target(self, detections):
        candidates = []

        for detection in detections:
            if int(detection.tag_id) != self.config.target_tag_id:
                continue

            if int(detection.hamming) > self.config.max_hamming:
                continue

            if float(detection.decision_margin) < self.config.min_decision_margin:
                continue

            area = self._tag_area_px(detection.corners.astype(np.float32))
            if area < self.config.min_tag_area_px:
                continue

            candidates.append(detection)

        if not candidates:
            self.lock_count = 0
            return None

        self.lock_count += 1
        if self.lock_count < self.config.lock_required_frames:
            return None

        return max(candidates, key=lambda d: d.decision_margin)

    @staticmethod
    def _estimate_tag_edge_px(corners: np.ndarray) -> float:
        p0, p1, p2, p3 = corners
        edges = [
            np.linalg.norm(p1 - p0),
            np.linalg.norm(p2 - p1),
            np.linalg.norm(p3 - p2),
            np.linalg.norm(p0 - p3),
        ]
        return float(np.mean(edges))

    @staticmethod
    def _tag_area_px(corners: np.ndarray) -> float:
        return float(cv2.contourArea(corners.astype(np.float32)))

    @staticmethod
    def _normalize_confidence(decision_margin: float) -> float:
        return max(0.0, min(float(decision_margin) / 100.0, 1.0))

    def _build_message(
        self,
        offset_x_px: float,
        offset_y_px: float,
        forward_cm: float | None,
        right_cm: float | None,
        yaw_deg: float,
        ready: bool,
    ) -> str:
        if ready:
            return "CENTERED + ALIGNED - READY TO LAND"

        commands: list[str] = []

        if forward_cm is not None and right_cm is not None:
            if abs(forward_cm) > self.config.position_deadband_cm:
                direction = "FORWARD" if forward_cm > 0 else "BACKWARD"
                commands.append(f"MOVE {direction} {abs(forward_cm):.1f}cm")

            if abs(right_cm) > self.config.position_deadband_cm:
                direction = "RIGHT" if right_cm > 0 else "LEFT"
                commands.append(f"MOVE {direction} {abs(right_cm):.1f}cm")
        else:
            if abs(offset_y_px) > self.config.position_deadband_px:
                direction = "FORWARD" if offset_y_px < 0 else "BACKWARD"
                commands.append(f"MOVE {direction}")

            if abs(offset_x_px) > self.config.position_deadband_px:
                direction = "RIGHT" if offset_x_px > 0 else "LEFT"
                commands.append(f"MOVE {direction}")

        if abs(yaw_deg) > self.config.yaw_deadband_deg:
            direction = "CW" if yaw_deg > 0 else "CCW"
            commands.append(f"ROTATE {direction} {abs(yaw_deg):.1f}deg")

        return " | ".join(commands) if commands else "HOLD"