"""Deterministic classification and numerical verification, without network I/O."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Literal

Level = Literal["low", "moderate", "high"]
LEVELS: tuple[Level, ...] = ("low", "moderate", "high")


@dataclass(frozen=True, slots=True)
class ClassScore:
    level: Level
    support: int
    predicted: int
    precision: float | None
    recall: float | None
    f1: float | None


@dataclass(frozen=True, slots=True)
class DetectionScore:
    threshold: Level
    hits: int
    misses: int
    false_alarms: int
    correct_negatives: int
    recall: float | None
    false_alarm_ratio: float | None
    false_positive_rate: float | None


@dataclass(frozen=True, slots=True)
class ClassificationScore:
    cases: int
    correct: int
    accuracy: float | None
    # Rows = observed, columns = predicted, in LEVELS order.
    confusion_matrix: tuple[tuple[int, ...], ...]
    classes: tuple[ClassScore, ...]
    macro_f1: float | None
    detection: tuple[DetectionScore, ...]


def _ratio(numerator: float, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def classify_pairs(pairs: Sequence[tuple[Level, Level]]) -> ClassificationScore:
    matrix = [[0] * 3 for _ in LEVELS]
    for observed, predicted in pairs:
        matrix[LEVELS.index(observed)][LEVELS.index(predicted)] += 1
    scores: list[ClassScore] = []
    for index, level in enumerate(LEVELS):
        tp = matrix[index][index]
        support = sum(matrix[index])
        predicted_count = sum(row[index] for row in matrix)
        scores.append(ClassScore(
            level, support, predicted_count, _ratio(tp, predicted_count),
            _ratio(tp, support), _ratio(2 * tp, support + predicted_count),
        ))
    detection: list[DetectionScore] = []
    for threshold in (1, 2):
        hits = misses = false_alarms = negatives = 0
        for observed_index, row in enumerate(matrix):
            for predicted_index, count in enumerate(row):
                if observed_index >= threshold and predicted_index >= threshold:
                    hits += count
                elif observed_index >= threshold:
                    misses += count
                elif predicted_index >= threshold:
                    false_alarms += count
                else:
                    negatives += count
        detection.append(DetectionScore(
            LEVELS[threshold], hits, misses, false_alarms, negatives,
            _ratio(hits, hits + misses), _ratio(false_alarms, hits + false_alarms),
            _ratio(false_alarms, false_alarms + negatives),
        ))
    f1_values = [score.f1 for score in scores if score.f1 is not None]
    correct = sum(matrix[index][index] for index in range(3))
    return ClassificationScore(
        len(pairs), correct, _ratio(correct, len(pairs)),
        tuple(tuple(row) for row in matrix), tuple(scores),
        sum(f1_values) / len(f1_values) if f1_values else None, tuple(detection),
    )


@dataclass(frozen=True, slots=True)
class NumericalScore:
    cases: int
    bias: float | None
    mae: float | None
    rmse: float | None


def numerical_pairs(pairs: Sequence[tuple[float, float]]) -> NumericalScore:
    """Pairs are (observed, predicted), already aligned and quality checked."""
    if any(not isfinite(value) for pair in pairs for value in pair):
        raise ValueError("verification values must be finite")
    errors = [predicted - observed for observed, predicted in pairs]
    if not errors:
        return NumericalScore(0, None, None, None)
    return NumericalScore(
        len(errors), sum(errors) / len(errors), sum(abs(error) for error in errors) / len(errors),
        sqrt(sum(error * error for error in errors) / len(errors)),
    )
