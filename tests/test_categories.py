"""Smoke tests: the game boots, registers its categories, and its data is sane."""

from memi_kr import app as app_module
from memi_kr.providers import categories as cat


def test_app_builds():
    assert app_module.app is not None


def test_link_preview_image_is_served():
    client = app_module.app.test_client()
    page = client.get("/").get_data(as_text=True)
    assert '<meta property="og:image" content="https://kr.memi.games/static/og.png">' in page
    assert 'content="summary_large_image"' in page
    resp = client.get("/static/og.png")
    assert resp.status_code == 200 and resp.mimetype == "image/png"


def test_expected_category_keys():
    keys = {p.key for p in cat.PROVIDERS}
    assert keys == {
        "culture:sights",
        "culture:food",
        "culture:folklore",
        "geography:districts",
        "geography:green",
        "people",
        "language",
        "marta’s tips",
    }


def test_language_cards_reveal_polish():
    lang = cat.Language()
    for en in lang.items:
        r = lang.get_image(en)
        assert r["name"] == cat.PHRASES[en]           # revealed answer is Polish
        assert r["image"].startswith("data:image/svg+xml")  # prompt is a text card


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


def test_marta_tips_have_details():
    tips = cat.MartasTips()
    for item in tips.items:
        tip = cat.TIPS[item]
        assert tip["area"] in cat.AREAS, f"{item} has an unknown area"
        assert tip["link"].startswith("https://"), f"{item} has no link"
        assert tips.get_tag(item).startswith(tip["area"])
        details = tips.get_details(item)
        assert details["text"], f"{item} has no text"
        assert details["area"]["url"].startswith("https://")
        # pins must land in central Kraków
        assert 50.04 < details["map"]["lat"] < 50.07, item
        assert 19.92 < details["map"]["lon"] < 19.96, item


def test_marta_tips_prefer_local_photo(tmp_path, monkeypatch):
    (tmp_path / "metal-wino.JPG").write_bytes(b"")
    monkeypatch.setattr(cat, "TIPS_DIR", tmp_path)
    r = cat.MartasTips().get_image("Metal Wino")
    assert r["image"] == "/static/tips/metal-wino.JPG"
    assert r["url"] == cat.TIPS["Metal Wino"]["link"]
