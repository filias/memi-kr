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


def test_every_district_has_a_prebuilt_card_and_credits():
    d = cat.Districts()
    credits = (cat.DISTRICTS_DIR / "CREDITS.md").read_text()
    for item in d.items:
        card = cat.DISTRICTS_DIR / f"{cat.district_slug(item)}.jpg"
        assert card.exists(), f"{item}: run scripts/build_district_cards.py"
        assert d.get_image(item)["image"] == f"/static/districts/{card.name}"
        assert f"`{card.name}`" in credits, f"{item} missing from CREDITS.md"


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


def test_maps_only_for_places_inside_krakow(monkeypatch):
    monkeypatch.setattr(
        cat.Green, "get_image", lambda self, item: {"url": "https://en.wikipedia.org/wiki/Vistula"}
    )
    # The Vistula's Wikidata point is its mouth on the Baltic: text, no map.
    monkeypatch.setattr(
        cat, "wiki_article", lambda title: {"intro": "A river.", "coords": (54.36, 18.95)}
    )
    assert cat.Green().get_details("Vistula") == {"text": "A river."}
    monkeypatch.setattr(
        cat, "wiki_article", lambda title: {"intro": "A river.", "coords": (50.0544, 19.9366)}
    )
    assert cat.Green().get_details("Vistula")["map"] == {
        "lat": 50.0544, "lon": 19.9366, "zoom": cat.Green.map_zoom
    }


def test_food_and_people_get_text_but_no_map(monkeypatch):
    monkeypatch.setattr(
        cat, "wiki_article", lambda title: {"intro": "Dumplings.", "coords": (50.06, 19.94)}
    )
    monkeypatch.setattr(
        cat.Food, "get_image", lambda self, item: {"url": "https://en.wikipedia.org/wiki/Pierogi"}
    )
    assert cat.Food().get_details("Pierogi") == {"text": "Dumplings."}


def test_article_failures_are_not_cached(monkeypatch):
    def boom(*a, **k):
        raise OSError("network down")

    monkeypatch.setattr(cat.requests, "get", boom)
    cat._article_cache.clear()
    assert cat.wiki_article("Wawel Castle") is None
    assert ("Wawel Castle", "en") not in cat._article_cache


def test_intro_drops_pronunciation_asides():
    raw = (
        "The Cloth Hall (Polish: Sukiennice, pronounced [sukʲɛˈɲːit͡sɛ]), is a "
        "historic cloth hall.\nSecond paragraph."
    )
    assert cat.wiki_intro(raw) == "The Cloth Hall is a historic cloth hall."
    nested = (
        "Napoleonka (Polish: [napɔlɛˈɔnka] ; colloquially kremówka (Polish: "
        "[krɛˈmufka] ), is a Polish type of cream pie. It is made of puff pastry, filled."
    )
    assert cat.wiki_intro(nested).startswith("Napoleonka is a Polish type of cream pie.")


def test_intro_trims_at_sentences_not_abbreviations():
    raw = "First sentence here. Second one is near St. Mary's altar. " + "Long " * 30
    assert cat.wiki_intro(raw, limit=80) == (
        "First sentence here. Second one is near St. Mary's altar."
    )


def test_every_person_has_a_krakow_line_in_the_panel(monkeypatch):
    monkeypatch.setattr(cat, "wiki_article", lambda title: {"intro": "Intro.", "coords": None})
    people = cat.People()
    for item in people.items:
        text = people.get_details(item)["text"]
        first = text.split("\n\n")[0]
        assert "Kraków" in first or "Kazimierz" in first, f"{item}: no Kraków link"
        assert text.endswith("Intro."), item


def test_language_audio_prefers_a_recording(tmp_path, monkeypatch):
    lang = cat.Language()
    monkeypatch.setattr(cat, "AUDIO_DIR", tmp_path)
    # No recording yet: the browser speaks the Polish.
    assert lang.get_audio("how are you?") == {"text": "jak się masz?", "lang": "pl-PL"}
    (tmp_path / "jak-sie-masz.m4a").write_bytes(b"")
    assert lang.get_audio("how are you?")["src"] == "/static/audio/jak-sie-masz.m4a"


def test_phrase_slugs_are_unique():
    slugs = [cat.phrase_slug(p) for p in cat.PHRASES.values()]
    assert len(slugs) == len(set(slugs))


def test_every_phrase_has_a_pronunciation_and_note():
    lang = cat.Language()
    assert set(cat.PHRASE_NOTES) == set(cat.PHRASES.values())
    for item in lang.items:
        text = lang.get_details(item)["text"]
        assert text.startswith("Say: ") and "\n\n" in text, item
