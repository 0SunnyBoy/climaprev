"""Paired moving-block resampling by calendar date, without fitting or acceptance."""

from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from math import isfinite
from random import Random


@dataclass(frozen=True, slots=True)
class BootstrapScore:
    estimate: float | None
    interval: tuple[float, float] | None
    repetitions: int
    undefined_repetitions: int
    calendar_dates: int
    segment_lengths: tuple[int, ...]
    requested_block_days: int
    effective_block_days: tuple[int, ...]
    seed: int
    confidence: float


def bootstrap_dates[T](cases: Sequence[T], *, day: Callable[[T], date],
                    statistic: Callable[[Sequence[T]], float | None], block_days: int = 7,
                    repetitions: int = 2000, seed: int = 20261016,
                    confidence: float = 0.95) -> BootstrapScore:
    """Keep all locations/leads of a sampled date together, separating calendar gaps.

    Short segments use their full length, explicitly disclosed. Undefined statistics
    or short segments suppress the interval rather than implying adequate support.
    The statistic and population must be specified before inspecting an experiment.
    """
    if block_days < 1 or repetitions < 2 or not 0 < confidence < 1:
        raise ValueError('invalid bootstrap parameters')
    if not cases:
        raise ValueError('bootstrap requires cases')
    grouped: dict[date, list[T]] = defaultdict(list)
    for case in cases:
        grouped[day(case)].append(case)
    segments: list[list[date]] = []
    for current in sorted(grouped):
        if not segments or current != segments[-1][-1] + timedelta(days=1):
            segments.append([])
        segments[-1].append(current)

    def evaluate(sample: Sequence[T]) -> float | None:
        value = statistic(sample)
        if value is not None and not isfinite(value):
            raise ValueError('bootstrap statistic must be finite or None')
        return value

    estimate = evaluate(cases)
    random = Random(seed)
    values = []
    undefined = 0
    effective = tuple(min(block_days, len(segment)) for segment in segments)
    for _ in range(repetitions):
        sample: list[T] = []
        for segment, size in zip(segments, effective, strict=True):
            dates: list[date] = []
            while len(dates) < len(segment):
                start = random.randrange(len(segment) - size + 1)
                dates.extend(segment[start:start+size])
            sample.extend(case for current in dates[:len(segment)] for case in grouped[current])
        value = evaluate(sample)
        if value is None:
            undefined += 1
        else:
            values.append(value)
    interval = None
    if estimate is not None and not undefined and all(size == block_days for size in effective):
        values.sort()

        def quantile(probability: float) -> float:
            position = probability * (len(values)-1)
            left = int(position)
            right = min(left+1, len(values)-1)
            return values[left] + (position-left)*(values[right]-values[left])

        alpha = (1-confidence)/2
        lower, upper = quantile(alpha), quantile(1-alpha)
        if lower < upper:
            interval = (lower, upper)
    return BootstrapScore(estimate, interval, repetitions, undefined, len(grouped),
                          tuple(map(len, segments)), block_days, effective, seed, confidence)
