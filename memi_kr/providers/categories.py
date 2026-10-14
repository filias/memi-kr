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
from urllib.parse import quote

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


class Sights(WikiImages, CategoryProvider):
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


class Districts(CategoryProvider):
    key = "geography:districts"
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


class Folklore(WikiImages, CategoryProvider):
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


class Green(WikiImages, CategoryProvider):
    key = "geography:green"
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
# the Rynek. Tag = area + Marta's note; "know more" opens the venue's own page. #
# Most venues have no Wikipedia article, so images are pinned Commons photos;  #
# a file in static/tips/<slug>.jpg takes precedence (and is the only source    #
# for venues with no Commons photo — those are skipped until one is added).    #
# --------------------------------------------------------------------------- #

TIPS_DIR = Path(__file__).resolve().parent.parent / "static" / "tips"
_PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

TIPS = {
    # name: (area, Marta's note, link, Commons file or None)
    "Kazimierz": (
        "Kazimierz",
        "the old Jewish district and the coolest place to be — most locals "
        "hang out here, and it's full of vintage shops",
        "https://en.wikipedia.org/wiki/Kazimierz",
        "Szeroka street,Kazimierz,Krakow,Poland.jpg",
    ),
    "Klezmer-Hois": (
        "Kazimierz",
        "Jewish food in Kazimierz",
        "https://klezmer.pl/klezmer-hois/",
        "KRAKÓW, AB. 126.JPG",
    ),
    "Hevre": (
        "Kazimierz",
        "café, restaurant and bar in an old prayer house — hevre means "
        "'friends' in Hebrew",
        "https://www.inyourpocket.com/poland/krakow/venues/hevre",
        "Hevre Tehilim Synagogue, interior, 18 Dow Ber Meisels Street, "
        "Kazimierz, Kraków, Poland.jpg",
    ),
    "Metal Wino": (
        "Kazimierz",
        "Hevre's tiny partner in crime next door — really great wine, and "
        "the food comes from Hevre",
        "https://www.wixcityguides.com/guide/krakow/food-%26-dining/wino-metal",
        None,
    ),
    "Okrąglak": (
        "Kazimierz",
        "for something quick — get a zapiekanka, they're huge",
        "https://www.wixcityguides.com/guide/krakow/food-%26-dining/okr%C4%85glak",
        "PlacNowy-Okrąglak-POL, Kraków.jpg",
    ),
    "Judah Food Market": (
        "Kazimierz",
        "food court with pierogi, kumpir, zapiekanka and coffee — you sit "
        "outside, so bring warm clothes",
        "https://www.instagram.com/judahfoodmarket/",
        None,
    ),
    "Bunkier Cafe": (
        "Rynek",
        "glass-walled café on the Planty, reopened after years — good coffee "
        "and breakfasts, next to the art gallery",
        "https://www.instagram.com/cafebunkier/",
        "Bunkier Cafe, Kraków, 2024, 01.jpg",
    ),
    "Nowa Prowincja": (
        "Rynek",
        "another iconic bar and coffee shop",
        "https://karnet.krakowculture.pl/531-krakow-nowa-prowincja",
        "Nowa Prowincja Kraków.jpg",
    ),
    "Kino Pod Baranami": (
        "Rynek",
        "a beautiful old cinema — catch Lalka in the small Red Room, with "
        "its wooden ceiling and red chairs",
        "https://www.kinopodbaranami.pl/english.php",
        "Kraków, Pałac Pod Baranami w Krakowie.jpg",
    ),
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
        _area, _note, link, commons_file = TIPS[item]
        slug = tip_slug(item)
        local = next(
            (p for p in sorted(TIPS_DIR.glob(f"{slug}.*")) if p.suffix.lower() in _PHOTO_EXTS),
            None,
        )
        if local:
            result = {"image": f"/static/tips/{local.name}"}
        elif commons_file:
            result = images.get_commons_file_image(commons_file)
            if not result:
                return None
            result = dict(result)
        else:
            return None
        result["name"] = item
        result["url"] = link
        return result

    def get_tag(self, item):
        area, note, _link, _file = TIPS[item]
        return f"{area} · {note}"


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
