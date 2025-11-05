"""
Tests for Python free-threaded mode (PEP 703) following guidelines from:
- Python Free-Threading Guide: https://py-free-threading.github.io/
- pytest-run-parallel: https://github.com/Quansight-Labs/pytest-run-parallel
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import TYPE_CHECKING, Callable, TypeVar

import pytest

from iso_week_date import IsoWeek, IsoWeekDate

if TYPE_CHECKING:
    from typing import Any

    from typing_extensions import TypeAlias

    AnyDict: TypeAlias = dict[str, Any]

pytestmark = pytest.mark.freethreaded

T = TypeVar("T")


NUM_THREADS = 4
NUM_ITERATIONS = 10


def run_threaded(
    test_func: Callable[[], T], num_threads: int = NUM_THREADS, num_iterations: int = NUM_ITERATIONS
) -> list[T]:
    """Run test function concurrently to detect thread safety issues."""
    results, errors = [], []

    def worker() -> T | None:
        try:
            return test_func()
        except Exception as e:  # noqa: BLE001  # pragma: no cover
            errors.append(e)
            return None

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_iterations)]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
    if errors:  # pragma: no cover
        pytest.fail(f"Thread safety violations: {len(errors)} errors. First error: {errors[0]}")
    return results


def test_concurrent_isoweek_creation() -> None:
    def create_week() -> IsoWeek:
        return IsoWeek("2023-W26")

    results = run_threaded(create_week)
    assert len(results) == NUM_ITERATIONS
    assert all(isinstance(r, IsoWeek) and str(r) == "2023-W26" for r in results)


def test_concurrent_isoweek_property_access() -> None:
    week = IsoWeek("2023-W26")

    def access_properties() -> AnyDict:
        return {"year": week.year, "week": week.week, "quarter": week.quarter, "str": str(week)}

    results = run_threaded(access_properties)
    expected = {"year": 2023, "week": 26, "quarter": 2, "str": "2023-W26"}
    assert all(r == expected for r in results)


def test_concurrent_isoweek_arithmetic() -> None:
    base_week = IsoWeek("2023-W26")

    def arithmetic_ops() -> AnyDict:
        return {"add": str(base_week + 1), "sub": str(base_week - 1), "diff": (base_week + 1) - (base_week - 1)}

    results = run_threaded(arithmetic_ops)
    expected = {"add": "2023-W27", "sub": "2023-W25", "diff": 2}
    assert all(r == expected for r in results)


def test_concurrent_isoweek_conversions() -> None:
    week = IsoWeek("2023-W26")

    def convert() -> AnyDict:
        return {"date": week.to_date(), "datetime": week.to_datetime(), "compact": week.to_compact()}

    results = run_threaded(convert)
    first_result = results[0]
    assert all(r == first_result for r in results)


def test_concurrent_isoweek_factory_methods() -> None:
    test_date = date(2023, 6, 26)

    def factory_methods() -> AnyDict:
        return {
            "from_date": str(IsoWeek.from_date(test_date)),
            "from_string": str(IsoWeek.from_string("2023-W26")),
            "from_values": str(IsoWeek.from_values(2023, 26)),
        }

    results = run_threaded(factory_methods)
    expected = {"from_date": "2023-W26", "from_string": "2023-W26", "from_values": "2023-W26"}
    assert all(r == expected for r in results)


def test_concurrent_isoweekdate_creation() -> None:
    def create_weekdate() -> IsoWeekDate:
        return IsoWeekDate("2023-W26-3")

    results = run_threaded(create_weekdate)
    assert len(results) == NUM_ITERATIONS
    assert all(isinstance(r, IsoWeekDate) and str(r) == "2023-W26-3" for r in results)


def test_concurrent_isoweekdate_property_access() -> None:
    weekdate = IsoWeekDate("2023-W26-3")

    def access_properties() -> AnyDict:
        return {"year": weekdate.year, "week": weekdate.week, "weekday": weekdate.weekday, "str": str(weekdate)}

    results = run_threaded(access_properties)
    expected = {"year": 2023, "week": 26, "weekday": 3, "str": "2023-W26-3"}
    assert all(r == expected for r in results)


def test_concurrent_isoweekdate_arithmetic() -> None:
    base_date = IsoWeekDate("2023-W26-3")

    def arithmetic_ops() -> AnyDict:
        return {"add_day": str(base_date + 1), "sub_day": str(base_date - 1), "add_week": str(base_date + 7)}

    results = run_threaded(arithmetic_ops)
    expected = {"add_day": "2023-W26-4", "sub_day": "2023-W26-2", "add_week": "2023-W27-3"}
    assert all(r == expected for r in results)


def test_concurrent_mixed_operations() -> None:
    def mixed_ops() -> list[Any]:
        week = IsoWeek("2023-W26")
        weekdate = IsoWeekDate("2023-W26-3")
        return [week.year, weekdate.weekday, str(week + 1), str(weekdate + 1), week.to_date(), weekdate.to_date()]

    results = run_threaded(mixed_ops)
    expected = results[0]
    assert all(r == expected for r in results)


def test_concurrent_shared_object_access() -> None:
    shared_week = IsoWeek("2023-W26")
    shared_date = IsoWeekDate("2023-W26-3")

    def access_shared() -> AnyDict:
        return {
            "week_year": shared_week.year,
            "week_str": str(shared_week),
            "date_weekday": shared_date.weekday,
            "date_str": str(shared_date),
        }

    results = run_threaded(access_shared)
    expected = {"week_year": 2023, "week_str": "2023-W26", "date_weekday": 3, "date_str": "2023-W26-3"}
    assert all(r == expected for r in results)


def test_stress_rapid_object_creation() -> None:
    def rapid_creation() -> int:
        objects = []
        for i in range(10):
            week = IsoWeek(f"2023-W{(i % 52) + 1:02d}")
            weekdate = IsoWeekDate(f"2023-W{(i % 52) + 1:02d}-{(i % 7) + 1}")
            _ = week.year + weekdate.weekday
            objects.extend([str(week), str(weekdate)])
        return len(objects)

    results = run_threaded(rapid_creation)
    assert all(r == NUM_ITERATIONS * 2 for r in results)


def test_gil_detection() -> None:
    if hasattr(sys, "_is_gil_enabled"):  # pragma: no cover
        _ = sys._is_gil_enabled()  # pyright: ignore[reportAttributeAccessIssue]
        week = IsoWeek("2023-W01")
        assert week.year == 2023  # noqa: PLR2004
    else:
        pytest.skip("GIL detection not available")


def test_true_parallelism() -> None:  # pragma: no cover
    if hasattr(sys, "_is_gil_enabled") and sys._is_gil_enabled():  # pyright: ignore[reportAttributeAccessIssue]
        pytest.skip("Test requires GIL to be disabled")

    def cpu_intensive() -> int:
        total = 0
        for i in range(500):
            week = IsoWeek(f"2023-W{(i % 52) + 1:02d}")
            total += week.year + week.week
            total += len(week.days)
        return total

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(cpu_intensive) for _ in range(NUM_THREADS)]
        results = [f.result() for f in futures]
    assert len(results) == NUM_THREADS
    assert all(isinstance(r, int) and r > 0 for r in results)
