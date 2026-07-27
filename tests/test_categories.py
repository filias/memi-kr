"""Smoke tests: the game boots, registers its categories, and its data is sane."""

from memi_kr import app as app_module
from memi_kr.providers import categories as cat


def test_app_builds():
    assert app_module.app is not None


def test_expected_category_keys():
    keys = {p.key for p in cat.PROVIDERS}
    assert keys == {
        "culture:sights",
        "culture:food",
        "culture:traditions",
        "geography:districts",
        "geography:green",
        "people",
    }


def test_every_sight_has_a_date():
    s = cat.Sights()
    for item in s.items:
        assert s.get_tag(item), f"sight {item} has no date"


def test_districts_use_maps():
    d = cat.Districts()
    for item in d.items:
        assert item in d.maps, f"district {item} has no locator map"


def test_no_empty_or_duplicate_items():
    for provider in cat.PROVIDERS:
        assert provider.items, f"{type(provider).__name__} has no items"
        assert len(provider.items) == len(set(provider.items)), (
            f"{type(provider).__name__} has duplicate items"
        )


def test_people_tags():
    people = cat.People()
    for item in people.items:
        assert people.get_tag(item), f"missing tag for {item}"
