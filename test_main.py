from collections import Counter
import pytest
from main import PropertyAllocator


def show_property(ratio: dict[str, int], db_count: dict[str, int], limit: int) -> list[str]:
    return PropertyAllocator(ratio, db_count, limit).show_property()


def assert_counts(result: list[str], expected_counts: dict[str, int]) -> None:
    assert Counter(result) == expected_counts


def test_show_property_limit_and_total_property_count_are_equal() -> None:
    limit: int = 20
    ratio: dict[str, int] = {"11": 20, "12": 50, "24": 30}
    db_count: dict[str, int] = {"11": 105, "12": 105, "24": 105}

    result: list[str] = show_property(ratio, db_count, limit)

    assert len(result) <= sum(db_count.values())
    assert_counts(result, Counter({"11": 4, "12": 10, "24": 6}))


def test_show_total_property_does_not_exceed_limit() -> None:
    limit: int = 24
    ratio: dict[str, int] = {"11": 20, "12": 60, "24": 20}
    db_count: dict[str, int] = {"11": 105, "12": 105, "24": 105}

    result: list[str] = show_property(ratio, db_count, limit)

    assert len(result) <= limit
    assert_counts(result, Counter({"12": 14, "24": 5, "11": 5}))


def test_show_property_insufficient_limit() -> None:
    limit: int = 1
    ratio: dict[str, int] = {"11": 60, "12": 25, "24": 15}
    db_count: dict[str, int] = {"11": 105, "12": 105, "24": 105}

    result: list[str] = show_property(ratio, db_count, limit)

    assert len(result) <= limit
    assert_counts(result, Counter({"11": 1}))


def test_show_property_total_property_greater_than_limit() -> None:
    limit: int = 12
    ratio: dict[str, int] = {"A": 1, "B": 20, "C": 20, "D": 40, "E": 18, "F": 1}
    db_count: dict[str, int] = {"A": 105, "B": 105, "C": 105, "D": 105, "E": 105, "F": 105}

    result: list[str] = show_property(ratio, db_count, limit)
    assert len(result) <= limit
    assert_counts(result, Counter({"D": 4, "C": 2, "B": 2, "E": 2, "F": 1, "A": 1}))



def test_show_property_large_dataset() -> None:
    limit: int = 17
    ratio: dict[str, int] = {"11": 25, "12": 35, "20": 10, "22": 10, "24": 15,"25": 5}
    db_count: dict[str, int] = {"11": 105, "12": 105, "20": 105, "22": 10, "24": 15, "25": 5}

    result: list[str] = show_property(ratio, db_count, limit)
    assert len(result) <= limit
    assert_counts(result, Counter({"11": 5, "12": 5, "20": 2, "22": 1, "24": 3, "25": 1}))


def test_show_property_handles_zero_db_count_and_redistributes() -> None:
    limit: int = 10
    ratio: dict[str, int] = {"11": 1, "12": 98, "24": 1}
    db_count: dict[str, int] = {"11": 0, "12": 80, "24": 50}

    result: list[str] = show_property(ratio, db_count, limit)

    assert len(result) <= limit
    assert_counts(result, Counter({"12": 9, "24": 1, "11": 0}))



def test_show_property_large_limit() -> None:
    limit: int = 192
    ratio: dict[str, int] = {"11": 25, "12": 35, "20": 10, "22": 10, "24": 15,"25": 5}
    db_count: dict[str, int] = {"11": 105, "12": 105, "20": 105, "22": 105, "24": 105, "25": 105}

    result: list[str] = show_property(ratio, db_count, limit)
    assert len(result) <= limit
    assert_counts(result, Counter({"11": 48, "12": 67, "20": 20, "22": 19, "24": 29, "25": 9}))



def test_show_property_db_exhausted_for_large_limit() -> None:
    limit: int = 192
    ratio: dict[str, int] = {"11": 1, "12": 98, "24": 1}
    db_count: dict[str, int] = {"11": 0, "12": 80, "24": 50}

    result: list[str] = show_property(ratio, db_count, limit)

    assert len(result) <= limit
    assert_counts(result, Counter({"12": 80, "24": 50, "11": 0}))









