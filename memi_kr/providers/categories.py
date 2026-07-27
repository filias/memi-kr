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
# Traditions & symbols — Kraków customs and emblems.                          #
# --------------------------------------------------------------------------- #


class Traditions(WikiImages, CategoryProvider):
    key = "culture:traditions"
    override_name = True
    items = [
        "Lajkonik",
        "Szopka",
        "Hejnał",
        "Wianki",
        "Coat of arms of Kraków",
    ]
    queries = {
        "Szopka": "Szopka krakowska",
        "Hejnał": "St. Mary's Trumpet Call",
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
        "Jordan Park": "Henryk Jordan Park",
        "Botanical Garden": "Botanical Garden of the Jagiellonian University",
    }


PROVIDERS = [
    Sights(),
    Food(),
    Traditions(),
    Districts(),
    Green(),
    People(),
]
for _provider in PROVIDERS:
    register(_provider)
