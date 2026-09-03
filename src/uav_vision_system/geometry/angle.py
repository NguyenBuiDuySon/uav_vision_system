import math

import numpy as np


def normalize_angle_deg(angle: float) -> float:
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle


def unit_vector(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm < 1e-6:
        return np.array([0.0, 0.0], dtype=np.float32)
    return vector / norm


def angle_deg_from_vector(vector: np.ndarray) -> float:
    return math.degrees(math.atan2(float(vector[1]), float(vector[0])))


def vector_from_angle_deg(angle_deg: float) -> np.ndarray:
    angle_rad = math.radians(angle_deg)
    return np.array(
        [math.cos(angle_rad), math.sin(angle_rad)],
        dtype=np.float32,
    )


def rotate_clockwise_90(vector: np.ndarray) -> np.ndarray:
    return np.array([-vector[1], vector[0]], dtype=np.float32)


def rotate_counter_clockwise_90(vector: np.ndarray) -> np.ndarray:
    return np.array([vector[1], -vector[0]], dtype=np.float32)