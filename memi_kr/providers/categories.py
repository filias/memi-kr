"""Kraków category providers.

The engine's default image lookup is strict (exact article title, must expose a
page image, no redirect-following). ``WikiImages`` relaxes that so natural
display names still land on the right Wikipedia article: it follows redirects
and falls back to a search when the exact title has no lead image.
"""

import base64
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote, unquote

import requests
from memi_engine import CategoryProvider, images, register

WIKIPEDIA_LANG = "en"
_WIKI_UA = {"User-Agent": "memi-krakow (+https://kr.memi.click)"}


@lru_cache(maxsize=1024)
def wiki_image(query, lang=WIKIPEDIA_LANG):
    """Resolve a name to its Wikipedia lead image + article URL, or ``None``."""
    api = f"https://{lang}.wikipedia.org/w/api.php"

    def fetch(extra):
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 800,
            "redirects": 1,
            **extra,
        }
        try:
            resp = requests.get(api, params=params, headers=_WIKI_UA, timeout=10)
            pages = resp.json().get("query", {}).get("pages", {})
        except Exception:
            return None
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                title = page.get("title", query)
                slug = quote(title.replace(" ", "_"))
                return {
                    "name": title,
                    "image": thumb,
                    "url": f"https://{lang}.wikipedia.org/wiki/{slug}",
                }
        return None

    return fetch({"titles": query}) or fetch(
        {"generator": "search", "gsrsearch": query, "gsrlimit": 1}
    )


class WikiImages:
    """Mixin: resolve images by a per-item query (falling back to the item name)."""

    queries: dict[str, str] = {}

    def get_image(self, item):
        return wiki_image(self.queries.get(item, item))


# Rough bounding box of Kraków. Wikipedia coordinates outside it belong to
# something other than the place on the card (the Vistula's are its mouth on
# the Baltic), so they get no map.
KRAKOW_BBOX = {"lat": (49.96, 50.13), "lon": (19.79, 20.22)}


_coords_cache = {}


def wiki_coords(title, lang=WIKIPEDIA_LANG):
    """Coordinates of the article's Wikidata item as ``(lat, lon)``, or ``None``.

    Wikidata rather than Wikipedia's own coordinates: those are often only
    "secondary" (absent from the default API answer) and sometimes plain wrong
    (MOCAK's sit 25 km west of the city).

    Answers are cached, including "no coordinates"; failed requests are not, so
    a network blip doesn't hide a card's map for good.
    """
    key = (title, lang)
    if key in _coords_cache:
        return _coords_cache[key]
    try:
        resp = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "prop": "pageprops",
                "ppprop": "wikibase_item",
                "redirects": 1,
                "titles": title,
            },
            headers=_WIKI_UA,
            timeout=5,
        )
        resp.raise_for_status()
        pages = resp.json()["query"]["pages"]
        qid = next(
            (p["pageprops"]["wikibase_item"] for p in pages.values() if "pageprops" in p),
            None,
        )
        coords = None
        if qid:
            resp = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbgetclaims",
                    "format": "json",
                    "entity": qid,
                    "property": "P625",
                },
                headers=_WIKI_UA,
                timeout=5,
            )
            resp.raise_for_status()
            claims = resp.json()["claims"].get("P625", [])
            if claims:
                value = claims[0]["mainsnak"]["datavalue"]["value"]
                coords = (value["latitude"], value["longitude"])
    except Exception:
        return None
    _coords_cache[key] = coords
    return coords


class WikiMap:
    """Mixin: a map pin in the details panel, from the card's Wikipedia article.

    The article is whatever the card's "know more" link points at, so it
    follows each provider's own title resolution (queries, pinned files, …).
    """

    map_zoom = 16

    def get_details(self, item):
        result = self.get_image(item)
        url = (result or {}).get("url", "")
        if "/wiki/" not in url:
            return None
        title = unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")
        coords = wiki_coords(title)
        if not coords:
            return None
        lat, lon = coords
        (lat_min, lat_max), (lon_min, lon_max) = KRAKOW_BBOX["lat"], KRAKOW_BBOX["lon"]
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            return None
        return {"map": {"lat": lat, "lon": lon, "zoom": self.map_zoom}}


# --------------------------------------------------------------------------- #
# Sights — landmarks, churches and museums, all the great things to see.       #
# --------------------------------------------------------------------------- #


SIGHT_DATES = {
    # landmarks
    "Wawel Castle": "14th century",
    "St. Mary's Basilica": "14th century",
    "Cloth Hall": "14th century",
    "Barbican": "1499",
    "St. Florian's Gate": "14th century",
    "Collegium Maius": "15th century",
    "Town Hall Tower": "14th century",
    "Main Square": "laid out 1257",
    "Planty Park": "1820s",
    "Kościuszko Mound": "1823",
    "Schindler's Factory": "1937",
    "Grunwald Monument": "1910",
    "Słowacki Theatre": "1893",
    # churches
    "Wawel Cathedral": "14th century",
    "Church of Saints Peter and Paul": "1619",
    "Church of St. Adalbert": "11th century",
    "St. Andrew's Church": "11th century",
    "Skałka": "1742",
    "Corpus Christi Basilica": "14th century",
    "St. Anne's Church": "1703",
    "St. Francis of Assisi Basilica": "13th century",
    # museums (founded)
    "Rynek Underground": "opened 2010",
    "National Museum": "founded 1879",
    "Czartoryski Museum": "founded 1796",
    "MOCAK": "opened 2011",
    "Ethnographic Museum": "founded 1911",
    "Polish Aviation Museum": "founded 1964",
    "Manggha": "opened 1994",
    # mounds
    "Piłsudski Mound": "1937",
    "Krakus Mound": "early medieval",
    "Wanda Mound": "early medieval",
    # synagogues
    "Old Synagogue": "15th century",
    "Remah Synagogue": "1553",
    "Tempel Synagogue": "1862",
    "Izaak Synagogue": "1644",
    "High Synagogue": "16th century",
    "Kupa Synagogue": "1643",
    "Popper Synagogue": "1620",
}


class Sights(WikiMap, WikiImages, CategoryProvider):
    key = "culture:sights"
    override_name = True
    tag_style = "plain"
    items = [
        # landmarks
        "Wawel Castle",
        "St. Mary's Basilica",
        "Cloth Hall",
        "Barbican",
        "St. Florian's Gate",
        "Collegium Maius",
        "Town Hall Tower",
        "Main Square",
        "Planty Park",
        "Kościuszko Mound",
        "Schindler's Factory",
        "Grunwald Monument",
        "Słowacki Theatre",
        # churches
        "Wawel Cathedral",
        "Church of Saints Peter and Paul",
        "Church of St. Adalbert",
        "St. Andrew's Church",
        "Skałka",
        "Corpus Christi Basilica",
        "St. Anne's Church",
        "St. Francis of Assisi Basilica",
        # museums
        "Rynek Underground",
        "National Museum",
        "Czartoryski Museum",
        "MOCAK",
        "Ethnographic Museum",
        "Polish Aviation Museum",
        "Manggha",
        # mounds (Kościuszko Mound is above)
        "Piłsudski Mound",
        "Krakus Mound",
        "Wanda Mound",
        # synagogues (Kazimierz)
        "Old Synagogue",
        "Remah Synagogue",
        "Tempel Synagogue",
        "Izaak Synagogue",
        "High Synagogue",
        "Kupa Synagogue",
        "Popper Synagogue",
    ]
    queries = {
        "St. Mary's Basilica": "St. Mary's Basilica, Kraków",
        "Cloth Hall": "Kraków Cloth Hall",
        "Barbican": "Kraków Barbican",
        "Town Hall Tower": "Town Hall Tower, Kraków",
        "Main Square": "Main Square, Kraków",
        "Schindler's Factory": "Oskar Schindler's Enamel Factory",
        "Grunwald Monument": "Grunwald Monument, Kraków",
        "Słowacki Theatre": "Juliusz Słowacki Theatre",
        "Church of Saints Peter and Paul": "Church of Saints Peter and Paul, Kraków",
        "Church of St. Adalbert": "Church of St. Adalbert, Kraków",
        "St. Andrew's Church": "Church of St. Andrew, Kraków",
        "Corpus Christi Basilica": "Corpus Christi Basilica, Kraków",
        "St. Anne's Church": "St. Anne's Church, Kraków",
        "St. Francis of Assisi Basilica": "Church of St. Francis of Assisi, Kraków",
        "National Museum": "National Museum, Kraków",
        "Ethnographic Museum": "Ethnographic Museum in Kraków",
        "Old Synagogue": "Old Synagogue, Kraków",
        "Tempel Synagogue": "Tempel Synagogue, Kraków",
        "Izaak Synagogue": "Isaac Synagogue, Kraków",
        "High Synagogue": "High Synagogue, Kraków",
    }
    # Items whose Wikipedia lead image is a logo (or otherwise poor) — pin a
    # Wikimedia Commons photo of the actual building instead.
    files = {
        "National Museum": "National Museum, Main Building, 1 May, 3 Avenue, Kraków, Poland.jpg",
    }

    def get_image(self, item):
        filename = self.files.get(item)
        if filename:
            result = images.get_commons_file_image(filename)
            if result:
                result = dict(result)
                result["name"] = item
                title = self.queries.get(item, item)
                result["url"] = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                return result
        return super().get_image(item)

    def get_tag(self, item):
        return SIGHT_DATES.get(item)


# --------------------------------------------------------------------------- #
# Districts — always shown as a locator map highlighting the area on the city, #
# so the game is "place the district" rather than "recognise a street photo".  #
# --------------------------------------------------------------------------- #


class Districts(WikiMap, CategoryProvider):
    key = "geography:districts"
    map_zoom = 14
    override_name = True
    light_bg = True
    items = [
        "Old Town",
        "Kazimierz",
        "Podgórze",
        "Nowa Huta",
        "Kleparz",
        "Zwierzyniec",
        "Krowodrza",
    ]
    # Wikimedia Commons locator maps (SIM areas of Kraków).
    maps = {
        "Old Town": "Obszar SIM Krakowa – Stare Miasto.svg",
        "Kazimierz": "Obszar SIM Krakowa – Kazimierz.svg",
        "Podgórze": "Obszar SIM Krakowa – Stare Podgórze.svg",
        "Nowa Huta": "Obszar SIM Krakowa – Nowa Huta.svg",
        "Kleparz": "Obszar SIM Krakowa – Kleparz.svg",
        "Zwierzyniec": "Obszar SIM Krakowa – Zwierzyniec.svg",
        "Krowodrza": "Obszar SIM Krakowa – Krowodrza.svg",
    }
    # Wikipedia article titles for the "know more" link.
    wiki = {
        "Old Town": "Kraków Old Town",
        "Kazimierz": "Kazimierz",
        "Podgórze": "Podgórze",
        "Nowa Huta": "Nowa Huta",
        "Kleparz": "Kleparz",
        "Zwierzyniec": "Zwierzyniec, Kraków",
        "Krowodrza": "Krowodrza",
    }

    def get_image(self, item):
        result = images.get_commons_file_image(self.maps[item])
        if not result:
            return None
        result = dict(result)
        result["name"] = item
        title = self.wiki.get(item, item)
        result["url"] = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        return result


# --------------------------------------------------------------------------- #
# Food — Kraków and Polish classics.                                          #
# --------------------------------------------------------------------------- #


class Food(WikiImages, CategoryProvider):
    key = "culture:food"
    override_name = True
    light_bg = True
    items = [
        "Obwarzanek",
        "Zapiekanka",
        "Pierogi",
        "Oscypek",
        "Bigos",
        "Sernik",
        "Makowiec",
        "Pączki",
        "Kiełbasa",
        "Kremówka",
    ]
    queries = {
        "Obwarzanek": "Obwarzanek krakowski",
        "Makowiec": "Poppy seed roll",
        "Kiełbasa": "Kielbasa",
    }


# --------------------------------------------------------------------------- #
# Folklore — Kraków's legends and folk traditions.                            #
# --------------------------------------------------------------------------- #


class Folklore(WikiMap, WikiImages, CategoryProvider):
    key = "culture:folklore"
    override_name = True
    items = [
        "Wawel Dragon",
        "Pan Twardowski",
        "Lajkonik",
        "Szopka",
        "Sigismund Bell",
    ]
    queries = {
        "Szopka": "Szopka krakowska",
    }


# --------------------------------------------------------------------------- #
# People — famous cracovians. Tag = what they are known for (shown on reveal). #
# --------------------------------------------------------------------------- #

PEOPLE = {
    # name: (known for, born–died)
    "Pope John Paul II": ("pope, Archbishop of Kraków", "1920–2005"),
    "Stanisław Lem": ("science-fiction writer", "1921–2006"),
    "Wisława Szymborska": ("poet, Nobel laureate", "1923–2012"),
    "Andrzej Wajda": ("film director", "1926–2016"),
    "Jan Matejko": ("painter", "1838–1893"),
    "Stanisław Wyspiański": ("playwright and painter", "1869–1907"),
    "Helena Modjeska": ("actress", "1840–1909"),
    "Veit Stoss": ("sculptor of the St. Mary's altarpiece", "c. 1447–1533"),
    "Czesław Miłosz": ("poet, Nobel laureate", "1911–2004"),
}


class People(WikiImages, CategoryProvider):
    key = "people"
    items = list(PEOPLE)
    tag_style = "plain"

    def get_tag(self, item):
        role, years = PEOPLE[item]
        return f"{role} · {years}"


# --------------------------------------------------------------------------- #
# Green — the river, parks and green spaces of the city.                      #
# --------------------------------------------------------------------------- #


class Green(WikiMap, WikiImages, CategoryProvider):
    key = "geography:green"
    map_zoom = 15
    override_name = True
    items = [
        "Vistula",
        "Vistula Boulevards",
        "Błonia",
        "Jordan Park",
        "Botanical Garden",
        "Kraków Zoo",
    ]
    queries = {
        "Vistula Boulevards": "Vistulan Boulevards, Kraków",
        "Jordan Park": "Henryk Jordan Park",
        "Botanical Garden": "Botanical Garden of the Jagiellonian University",
    }


# --------------------------------------------------------------------------- #
# Language — read the English phrase (rendered as a text card), reveal the     #
# Polish. Around 20 of the most useful words and greetings.                    #
# --------------------------------------------------------------------------- #

PHRASES = {
    "hello": "cześć",
    "good morning": "dzień dobry",
    "good evening": "dobry wieczór",
    "good night": "dobranoc",
    "goodbye": "do widzenia",
    "see you": "do zobaczenia",
    "thank you": "dziękuję",
    "please": "proszę",
    "you're welcome": "nie ma za co",
    "yes": "tak",
    "no": "nie",
    "sorry": "przepraszam",
    "how are you?": "jak się masz?",
    "cheers!": "na zdrowie!",
    "I don't understand": "nie rozumiem",
    "help!": "pomocy!",
    "water": "woda",
    "beer": "piwo",
    "friend": "przyjaciel",
    "love": "miłość",
}


def _text_card(text):
    """Render a short English phrase as an SVG data-URI to use as the card image."""
    size = min(60, max(28, 780 // max(len(text), 1)))
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" '
        'viewBox="0 0 640 420">'
        '<rect width="640" height="420" fill="#f7f5f0"/>'
        f'<text x="320" y="140" text-anchor="middle" dominant-baseline="middle" '
        f"font-family=\"Georgia, 'Times New Roman', serif\" font-size=\"{size}\" "
        f'fill="#223344">{safe}</text>'
        "</svg>"
    )
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + b64


class Language(CategoryProvider):
    key = "language"
    light_bg = True
    items = list(PHRASES)

    def get_image(self, item):
        polish = PHRASES[item]
        return {
            "name": polish,
            "image": _text_card(item),
            "url": f"https://en.wiktionary.org/wiki/{quote(polish)}",
        }


# --------------------------------------------------------------------------- #
# Marta's tips — a local's battle-tested favourites in Kazimierz and around    #
# the Rynek. The card tag is short (area · tag); the enriched layout's details #
# panel carries Marta's own words, a link to the area and a map pin. "know     #
# more" opens the venue's own page.                                            #
# Most venues have no Wikipedia article, so images are pinned Commons photos;  #
# a file in static/tips/<slug>.<ext> takes precedence (and is the only source  #
# for venues with no Commons photo — those are skipped until one is added).    #
# --------------------------------------------------------------------------- #

TIPS_DIR = Path(__file__).resolve().parent.parent / "static" / "tips"
_PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

AREAS = {
    "Kazimierz": "https://en.wikipedia.org/wiki/Kazimierz",
    "Rynek": "https://en.wikipedia.org/wiki/Main_Square,_Krak%C3%B3w",
}

TIPS = {
    # Pins are OpenStreetMap coordinates of the venue (or its address).
    "Kazimierz": {
        "area": "Kazimierz",
        "tag": "the coolest place to be",
        "text": (
            "Kraków is special not only because of Poles but also because of "
            "its long Jewish history, centred in Kazimierz. Most beautiful, "
            "imho — and nowadays most locals hang out here.\n\n"
            "For fashion aficionados, there are looooots of vintage shops."
        ),
        "link": "https://en.wikipedia.org/wiki/Kazimierz",
        "photo": "Szeroka Street in Kraków, 2024 (01).jpg",
        "pin": (50.0531122, 19.9473440, 15),
    },
    "Klezmer-Hois": {
        "area": "Kazimierz",
        "tag": "Jewish food",
        "text": "Jewish food in Kazimierz.",
        "link": "https://klezmer.pl/klezmer-hois/",
        "photo": "KRAKÓW, AB. 126.JPG",
        "pin": (50.0532169, 19.9482568, 17),
    },
    "Hevre": {
        "area": "Kazimierz",
        "tag": "café-bar in an old synagogue",
        "text": (
            "Café, restaurant and bar in an old synagogue. Hevre means "
            "'friends' in Hebrew :)"
        ),
        "link": "https://www.inyourpocket.com/poland/krakow/venues/hevre",
        "photo": (
            "Hevre Tehilim Synagogue, interior, 18 Dow Ber Meisels Street, "
            "Kazimierz, Kraków, Poland.jpg"
        ),
        "pin": (50.0511806, 19.9433767, 17),
    },
    "Metal Wino": {
        "area": "Kazimierz",
        "tag": "wine bar next to Hevre",
        "text": (
            "Wine bar, a much smaller partner in crime to Hevre :) Really great "
            "wine, really cool girl working there. They're right next to Hevre "
            "(you actually go to the toilet in Hevre), and they serve food from "
            "there as well."
        ),
        "link": "https://www.wixcityguides.com/guide/krakow/food-%26-dining/wino-metal",
        "photo": None,
        "pin": (50.0511275, 19.9432505, 17),
    },
    "Okrąglak": {
        "area": "Kazimierz",
        "tag": "get a zapiekanka",
        "text": (
            "If you want something quick and fast-foody to eat, you go there. "
            "You take a zapiekanka — they're pretty huge :D"
        ),
        "link": "https://www.wixcityguides.com/guide/krakow/food-%26-dining/okr%C4%85glak",
        "photo": "PlacNowy-Okrąglak-POL, Kraków.jpg",
        "pin": (50.0517373, 19.9446185, 17),
    },
    "Judah Food Market": {
        "area": "Kazimierz",
        "tag": "food court, bring warm clothes",
        "text": (
            "Another iconic place in Kazimierz. It's a food court: you can grab "
            "pierogi, kumpir (a huge potato with stuff, I love it), zapiekanka, "
            "coffee and more. You sit outside, so grab warm clothes :D"
        ),
        "link": "https://www.instagram.com/judahfoodmarket/",
        "photo": None,
        "pin": (50.0502904, 19.9485371, 17),
    },
    "Bunkier Cafe": {
        "area": "Rynek",
        "tag": "glass café on the Planty",
        "text": (
            "It's on the Planty, the huge park around the city centre — Planty "
            "itself is worth a walk. It used to be called Bunkier Sztuki and was "
            "closed for years; they reopened it two years ago, renovated. It's a "
            "coffee shop behind glass walls, so you sit inside but feel like "
            "you're outside. Good coffee, breakfasts, etc. It's right next to "
            "the art gallery as well."
        ),
        "link": "https://www.instagram.com/cafebunkier/",
        "photo": "Bunkier Sztuki w kwietniu 2026 r. 04 kawiarnia.jpg",
        "pin": (50.0635805, 19.9344469, 17),
    },
    "Nowa Prowincja": {
        "area": "Rynek",
        "tag": "iconic bar & coffee shop",
        "text": "Another iconic bar / coffee shop.",
        "link": "https://karnet.krakowculture.pl/531-krakow-nowa-prowincja",
        "photo": "Nowa Prowincja Kraków.jpg",
        "pin": (50.0604258, 19.9361543, 17),
    },
    "Kino Pod Baranami": {
        "area": "Rynek",
        "tag": "a beautiful old cinema",
        "text": (
            "A very beautiful movie theatre. You can watch Lalka there, a Polish "
            "movie based on Prus's book — one every Pole studied in high school. "
            "It's what everyone talks about these days: there's a new Netflix "
            "series and the movie, almost at the same time. I haven't seen the "
            "movie yet, but I hear it's top notch.\n\n"
            "One screening room has a decorative wooden ceiling and red chairs, "
            "and it's quite small. It's called the Red Room — not to be confused "
            "with redrum from The Shining..."
        ),
        "link": "https://www.kinopodbaranami.pl/english.php",
        "photo": "Kraków, Pałac Pod Baranami w Krakowie.jpg",
        "pin": (50.0616001, 19.9352018, 17),
    },
}


def tip_slug(name):
    """``"Judah Food Market"`` -> ``"judah-food-market"`` (local photo filename)."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "-".join(ascii_name.lower().split())


class MartasTips(CategoryProvider):
    key = "marta’s tips"
    override_name = True
    tag_style = "plain"
    items = list(TIPS)

    def get_image(self, item):
        tip = TIPS[item]
        slug = tip_slug(item)
        local = next(
            (p for p in sorted(TIPS_DIR.glob(f"{slug}.*")) if p.suffix.lower() in _PHOTO_EXTS),
            None,
        )
        if local:
            result = {"image": f"/static/tips/{local.name}"}
        elif tip["photo"]:
            result = images.get_commons_file_image(tip["photo"])
            if not result:
                return None
            result = dict(result)
        else:
            return None
        result["name"] = item
        result["url"] = tip["link"]
        return result

    def get_tag(self, item):
        tip = TIPS[item]
        return f"{tip['area']} · {tip['tag']}"

    def get_details(self, item):
        tip = TIPS[item]
        lat, lon, zoom = tip["pin"]
        return {
            "text": tip["text"],
            "area": {"name": tip["area"], "url": AREAS[tip["area"]]},
            "map": {"lat": lat, "lon": lon, "zoom": zoom},
        }


PROVIDERS = [
    Sights(),
    Food(),
    Folklore(),
    Districts(),
    Green(),
    People(),
    Language(),
    MartasTips(),
]
for _provider in PROVIDERS:
    register(_provider)
