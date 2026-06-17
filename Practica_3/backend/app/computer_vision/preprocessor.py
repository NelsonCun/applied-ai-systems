from pathlib import Path

import cv2
import numpy as np


def resize_for_ocr(
    image: np.ndarray,
) -> np.ndarray:
    height, width = image.shape[:2]

    target_width = 2200

    if width >= target_width:
        return image

    scale = min(
        2.5,
        target_width / max(width, 1),
    )

    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC,
    )


def correct_skew(
    gray_image: np.ndarray,
) -> tuple[np.ndarray, float]:
    inverted = cv2.bitwise_not(gray_image)

    _, threshold = cv2.threshold(
        inverted,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU,
    )

    coordinates = np.column_stack(
        np.where(threshold > 0)
    )

    if len(coordinates) < 100:
        return gray_image, 0.0

    angle = cv2.minAreaRect(
        coordinates
    )[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) > 15:
        return gray_image, 0.0

    height, width = gray_image.shape[:2]
    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0,
    )

    rotated = cv2.warpAffine(
        gray_image,
        rotation_matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return rotated, float(angle)


def preprocess_image(
    image: np.ndarray,
) -> tuple[np.ndarray, dict]:
    resized = resize_for_ocr(image)

    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_BGR2GRAY,
    )

    deskewed, angle = correct_skew(gray)

    denoised = cv2.fastNlMeansDenoising(
        deskewed,
        None,
        h=10,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        41,
        15,
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2),
    )

    processed = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
    )

    metadata = {
        "original_width": int(image.shape[1]),
        "original_height": int(image.shape[0]),
        "processed_width": int(processed.shape[1]),
        "processed_height": int(processed.shape[0]),
        "deskew_angle": round(angle, 3),
    }

    return processed, metadata


def save_processed_image(
    image: np.ndarray,
    output_path: str,
) -> None:
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    written = cv2.imwrite(
        str(path),
        image,
    )

    if not written:
        raise RuntimeError(
            f"No fue posible guardar la imagen procesada: {path}"
        )
