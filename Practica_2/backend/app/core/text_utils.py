import re
import unicodedata
from difflib import SequenceMatcher


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )

    lowercase = without_accents.lower()

    alphanumeric = re.sub(
        r"[^a-z0-9\s]",
        " ",
        lowercase,
    )

    return " ".join(alphanumeric.split())


def calculate_similarity(
    first_text: str,
    second_text: str,
) -> float:
    sequence_score = SequenceMatcher(
        None,
        first_text,
        second_text,
    ).ratio()

    first_tokens = set(first_text.split())
    second_tokens = set(second_text.split())

    if not first_tokens or not second_tokens:
        return sequence_score

    intersection = first_tokens & second_tokens
    union = first_tokens | second_tokens

    jaccard_score = len(intersection) / len(union)
    coverage_score = len(intersection) / min(
        len(first_tokens),
        len(second_tokens),
    )

    token_score = (
        jaccard_score + coverage_score
    ) / 2

    return max(sequence_score, token_score)
