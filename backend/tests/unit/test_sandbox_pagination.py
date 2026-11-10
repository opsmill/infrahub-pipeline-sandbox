from dataclasses import dataclass

import pytest

from infrahub.sandbox_pagination import count_pages


@dataclass
class CountPagesTestCase:
    name: str
    total_items: int
    page_size: int
    expected: int


COUNT_PAGES_TEST_CASES: list[CountPagesTestCase] = [
    CountPagesTestCase(name="partial_last_page_is_counted", total_items=21, page_size=10, expected=3),
    CountPagesTestCase(name="fewer_items_than_page_size_needs_one_page", total_items=5, page_size=10, expected=1),
    CountPagesTestCase(name="one_item_over_a_full_page_needs_two_pages", total_items=11, page_size=10, expected=2),
    CountPagesTestCase(name="exact_multiple_fills_every_page", total_items=20, page_size=10, expected=2),
    CountPagesTestCase(name="single_full_page", total_items=10, page_size=10, expected=1),
    CountPagesTestCase(name="one_item_per_page", total_items=1, page_size=1, expected=1),
    CountPagesTestCase(name="no_items_needs_no_pages", total_items=0, page_size=10, expected=0),
]


@pytest.mark.parametrize(
    "test_case",
    [pytest.param(tc, id=tc.name) for tc in COUNT_PAGES_TEST_CASES],
)
def test_count_pages_covers_every_item(test_case: CountPagesTestCase) -> None:
    assert count_pages(total_items=test_case.total_items, page_size=test_case.page_size) == test_case.expected
