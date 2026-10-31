"""Audit published monthly totals without changing observational data or labels."""

import argparse
import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from climaprev.tools.inmet_observations import StationHour, parse_station_csv


def observation_day_rain(raw: bytes, *, previous_raw: bytes, station: str,
                         month: date) -> dict[str, Any]:
    """Rain labelled by the date it ends at 12 UTC, retaining both annual parents."""
    if month.day != 1:
        raise ValueError('month must be the first day')
    current_metadata, current = parse_station_csv(raw, expected_station=station)
    previous_metadata, previous = parse_station_csv(previous_raw, expected_station=station)
    by_endpoint: dict[datetime, StationHour] = {}
    for row in previous + current:
        if row.endpoint in by_endpoint:
            raise ValueError('annual parents have overlapping endpoints')
        by_endpoint[row.endpoint] = row
    next_month = (month.replace(day=28)+timedelta(days=4)).replace(day=1)
    day = month
    days: list[dict[str, Any]] = []
    while day < next_month:
        end = datetime.combine(day, time(12), UTC)
        start = end-timedelta(days=1)
        stamps = [start+timedelta(hours=index) for index in range(1, 25)]
        missing = [stamp.isoformat() for stamp in stamps
                   if stamp not in by_endpoint or by_endpoint[stamp].rain_mm is None]
        total = None if missing else round(sum(
            by_endpoint[stamp].rain_mm or 0. for stamp in stamps), 6)
        days.append({'date':day.isoformat(), 'start_utc':start.isoformat(),
                     'end_utc':end.isoformat(), 'expected_hours':24,
                     'missing_endpoints_utc':missing, 'rain_mm':total})
        day += timedelta(days=1)
    complete = all(row['rain_mm'] is not None for row in days)
    return {'convention':'observation-day-ending-12utc-v1',
            'interval':'previous day 12 UTC exclusive; labelled day 12 UTC inclusive',
            'month':month.isoformat(), 'days':days,
            'monthly_rain_mm': round(sum(row['rain_mm'] for row in days), 6) if complete else None,
            'parents':[{'sha256':hashlib.sha256(parent).hexdigest(), 'station':metadata}
                       for parent, metadata in ((previous_raw, previous_metadata),
                                                (raw, current_metadata))],
            'coordinates_identical':all(previous_metadata[key] == current_metadata[key]
                                        for key in ('latitude','longitude','altitude')),
            'scientific_approval':False, 'calibration_ready':False}


def reconcile(raw: bytes, *, station: str, month: date,
              published_rain_mm: float) -> dict[str, Any]:
    """Compare explicit UTC window conventions; matching is not scientific approval."""
    if month.day != 1:
        raise ValueError("month must be the first day")
    if not 0 <= published_rain_mm < float('inf'):
        raise ValueError("published rain must be finite and nonnegative")
    metadata, hours = parse_station_csv(raw, expected_station=station)
    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    by_endpoint = {hour.endpoint: hour for hour in hours}
    windows = []
    # Fixed diagnostics, not a search for a boundary that matches the bulletin.
    for label, offset, preceding in (
        ('utc-timestamp', 0, False),
        ('utc-preceding-hour', 0, True),
        ('belem-civil-preceding-hour', 3, True),
        ('12utc-preceding-hour-diagnostic', 12, True),
    ):
        start = datetime.combine(month, time.min, UTC) + timedelta(hours=offset)
        end = datetime.combine(next_month, time.min, UTC) + timedelta(hours=offset)
        cursor = start + timedelta(hours=int(preceding))
        missing = []
        values = []
        while cursor <= end if preceding else cursor < end:
            row = by_endpoint.get(cursor)
            if row is None or row.rain_mm is None:
                missing.append(cursor.isoformat())
            else:
                values.append(row.rain_mm)
            cursor += timedelta(hours=1)
        total = round(sum(values), 6) if not missing else None
        daily_windows = []
        day_start = start
        while day_start < end:
            first = day_start + timedelta(hours=int(preceding))
            stamps = [first + timedelta(hours=index) for index in range(24)]
            rain = [by_endpoint[stamp].rain_mm for stamp in stamps
                    if stamp in by_endpoint and by_endpoint[stamp].rain_mm is not None]
            daily_windows.append({
                'window_start_date': day_start.date().isoformat(),
                'start_utc': day_start.isoformat(),
                'end_utc': (day_start+timedelta(days=1)).isoformat(),
                'valid_hours': len(rain),
                'rain_mm': round(sum(value for value in rain if value is not None), 6)
                if len(rain) == 24 else None,
            })
            day_start += timedelta(days=1)
        windows.append({'convention': label, 'start_utc': start.isoformat(),
                        'end_utc': end.isoformat(), 'endpoints_expected':
                        int((end-start).total_seconds()/3600),
                        'endpoints_valid': len(values), 'missing': missing,
                        'rain_mm': total, 'difference_from_bulletin_mm':
                        None if total is None else round(total-published_rain_mm, 6),
                        'daily_windows': daily_windows})
    return {'station': metadata, 'month': month.isoformat(),
            'csv_sha256': hashlib.sha256(raw).hexdigest(),
            'published_rain_mm': published_rain_mm, 'windows': windows,
            'scientific_approval': False, 'calibration_ready': False,
            'limitation': 'Window diagnostics cannot establish source revisions, sensor quality '
                          'or the bulletin aggregation convention.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--station-csv', type=Path, required=True)
    parser.add_argument('--station', required=True)
    parser.add_argument('--month', type=date.fromisoformat, required=True)
    parser.add_argument('--published-rain-mm', type=float, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--previous-station-csv', type=Path)
    args = parser.parse_args()
    report = reconcile(args.station_csv.read_bytes(), station=args.station,
                       month=args.month, published_rain_mm=args.published_rain_mm)
    if args.previous_station_csv:
        report['observation_day_12utc'] = observation_day_rain(
            args.station_csv.read_bytes(), previous_raw=args.previous_station_csv.read_bytes(),
            station=args.station, month=args.month)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
