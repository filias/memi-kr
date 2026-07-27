"""Kraków category providers.

The engine's default image lookup is strict (exact article title, must expose a
page image, no redirect-following). ``WikiImages`` relaxes that so natural
display names still land on the right Wikipedia article: it follows redirects
and falls back to a search when the exact title has no lead image.
"""

from functools import lru_cache
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


class Sights(WikiImages, CategoryProvider):
    key = "culture:sights"
    override_name = True
    items = [
        # landmarks
        "Wawel Castle",
        "St. Mary's Basilica",
        "Cloth Hall",
        "Barbican",
        "St. Florian's Gate",
        "Collegium Maius",
        "Wawel Dragon",
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
    }


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
# People — famous cracovians. Tag = what they are known for (shown on reveal). #
# --------------------------------------------------------------------------- #

PEOPLE = {
    "Pope John Paul II": "pope, Archbishop of Kraków",
    "Stanisław Lem": "science-fiction writer",
    "Wisława Szymborska": "poet, Nobel laureate",
    "Andrzej Wajda": "film director",
    "Jan Matejko": "painter",
    "Stanisław Wyspiański": "playwright and painter",
    "Helena Modjeska": "actress",
    "Veit Stoss": "sculptor of the St. Mary's altarpiece",
    "Czesław Miłosz": "poet, Nobel laureate",
}


class People(WikiImages, CategoryProvider):
    key = "people"
    items = list(PEOPLE)
    tag_style = "plain"

    def get_tag(self, item):
        return PEOPLE.get(item)


PROVIDERS = [
    Sights(),
    Food(),
    Districts(),
    People(),
]
for _provider in PROVIDERS:
    register(_provider)
