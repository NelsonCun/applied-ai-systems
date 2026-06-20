from typing import Any

import numpy as np
import pytesseract
from pytesseract import Output


def extract_text(
    image: np.ndarray,
    language: str,
) -> dict[str, Any]:
    config = (
        "--oem 3 "
        "--psm 6 "
        "-c preserve_interword_spaces=1"
    )

    data = pytesseract.image_to_data(
        image,
        lang=language,
        config=config,
        output_type=Output.DICT,
    )

    text = pytesseract.image_to_string(
        image,
        lang=language,
        config=config,
    ).strip()

    confidences: list[float] = []

    for raw_confidence in data.get(
        "conf",
        [],
    ):
        try:
            confidence = float(raw_confidence)
        except (TypeError, ValueError):
            continue

        if confidence >= 0:
            confidences.append(confidence)

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    recognized_words = [
        word.strip()
        for word in data.get("text", [])
        if word and word.strip()
    ]

    return {
        "text": text,
        "confidence": round(
            average_confidence,
            2,
        ),
        "recognized_words": len(
            recognized_words
        ),
    }
