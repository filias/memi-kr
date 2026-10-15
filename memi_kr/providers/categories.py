"""Kraków category providers.

The engine's default image lookup is strict (exact article title, must expose a
page image, no redirect-following). ``WikiImages`` relaxes that so natural
display names still land on the right Wikipedia article: it follows redirects
and falls back to a search when the exact title has no lead image.
"""

import base64
import re
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


# Rough bounds of Kraków for the details panel's map. Wikidata coordinates
# outside it belong to something other than the place on the card (the
# Vistula's are its mouth on the Baltic), so they get no map.
KRAKOW_BOUNDS = ((49.96, 50.13), (19.79, 20.22))


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
    map_zoom = 16
    map_bounds = KRAKOW_BOUNDS
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
# Districts — a photo of the place with a locator-map inset, zoomed around the #
# district, in the corner: what it looks like and roughly where it is. The     #
# composites are prebuilt by scripts/build_district_cards.py into              #
# static/districts/ (credits alongside); a district without one falls back to  #
# the bare locator map.                                                        #
# --------------------------------------------------------------------------- #

DISTRICTS_DIR = Path(__file__).resolve().parent.parent / "static" / "districts"

DISTRICTS = {
    # name: SIM-area locator map (Commons "Obszar SIM Krakowa – <area>.svg"),
    # Wikipedia article, Commons photo.
    "Old Town": {
        "area": "Stare Miasto",
        "wiki": "Kraków Old Town",
        "photo": "Floriańska Street in Kraków, 2024 (01).jpg",
    },
    "Kazimierz": {
        "area": "Kazimierz",
        "wiki": "Kazimierz",
        "photo": "Szeroka Street in Kraków, 2024 (01).jpg",
    },
    "Podgórze": {
        "area": "Stare Podgórze",
        "wiki": "Podgórze",
        "photo": "Podgórze Market Square in Kraków 1.jpg",
    },
    "Nowa Huta": {
        "area": "Nowa Huta",
        "wiki": "Nowa Huta",
        "photo": "Nowa Huta - Plac Centralny z lotu ptaka.jpg",
    },
    "Kleparz": {
        "area": "Kleparz",
        "wiki": "Kleparz",
        "photo": "2019-07-06 Market Square in Kleparz, Kraków 1.jpg",
    },
    "Zwierzyniec": {
        "area": "Zwierzyniec",
        "wiki": "Zwierzyniec, Kraków",
        "photo": (
            "Church of St. Augustine and St. John the Baptist and Norbertine "
            "Sisters monastery, 88 Kościuszki Street, Kraków, Poland.jpg"
        ),
    },
    "Krowodrza": {
        "area": "Krowodrza",
        "wiki": "Krowodrza",
        "photo": "Inwalidów square, view from E, Kraków, Poland.jpg",
    },
    "Dębniki": {
        "area": "Dębniki",
        "wiki": "Dębniki, Kraków",
        "photo": "Dębniki, rynek.jpg",
    },
    "Grzegórzki": {
        "area": "Grzegórzki",
        "wiki": "Grzegórzki, Kraków (district)",
        "photo": (
            "Church of StCasimir Jagiellon, 78 Grzegórzecka street,Grzegorzki,"
            "Krakow,Poland.jpg"
        ),
    },
    "Płaszów": {
        "area": "Płaszów",
        "wiki": "Płaszów",
        "photo": "Memorial walk at Płaszów concentration camp (1490981767).jpg",
    },
    "Tyniec": {
        "area": "Tyniec",
        "wiki": "Tyniec",
        "photo": "20200529 Widok ze Skały Okrążek na Opactwo w Tyńcu 1735 2128.jpg",
    },
    "Łagiewniki": {
        "area": "Łagiewniki",
        "wiki": "Łagiewniki-Borek Fałęcki",
        "photo": "Church of Divine Mercy, 3 Siostry Faustyny street, Łagiewniki, Kraków Poland.jpg",
    },
}


def district_slug(name):
    """``"Łagiewniki"`` -> ``"lagiewniki"`` (composite filename)."""
    folded = unicodedata.normalize("NFKD", name.replace("ł", "l").replace("Ł", "L"))
    return "-".join(folded.encode("ascii", "ignore").decode().lower().split())


class Districts(CategoryProvider):
    key = "geography:districts"
    map_zoom = 14
    map_bounds = KRAKOW_BOUNDS
    override_name = True
    items = list(DISTRICTS)

    def get_image(self, item):
        district = DISTRICTS[item]
        composite = DISTRICTS_DIR / f"{district_slug(item)}.jpg"
        if composite.exists():
            result = {"image": f"/static/districts/{composite.name}"}
        else:
            result = images.get_commons_file_image(
                f"Obszar SIM Krakowa – {district['area']}.svg"
            )
            if not result:
                return None
            result = dict(result)
        result["name"] = item
        title = district["wiki"]
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
    map_zoom = 16
    map_bounds = KRAKOW_BOUNDS
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
    # name: (known for, born–died, their Kraków link — leads the details panel,
    # since a Wikipedia intro doesn't always mention the city)
    "Pope John Paul II": (
        "pope, Archbishop of Kraków",
        "1920–2005",
        "Came to Kraków in 1938 to study at the Jagiellonian University, and was "
        "Archbishop of Kraków from 1964 until his election as pope in 1978.",
    ),
    "Stanisław Lem": (
        "science-fiction writer",
        "1921–2006",
        "Settled in Kraków after the war and lived there for the rest of his "
        "life; he is buried in the city's Salwator Cemetery.",
    ),
    "Wisława Szymborska": (
        "poet, Nobel laureate",
        "1923–2012",
        "Lived in Kraków from the age of eight until her death, and studied at "
        "the Jagiellonian University.",
    ),
    "Andrzej Wajda": (
        "film director",
        "1926–2016",
        "Studied painting at Kraków's Academy of Fine Arts, and founded the "
        "city's Manggha Museum of Japanese Art and Technology.",
    ),
    "Jan Matejko": (
        "painter",
        "1838–1893",
        "Born in Kraków, he studied at the city's School of Fine Arts and later "
        "ran it; today it is the Jan Matejko Academy of Fine Arts.",
    ),
    "Stanisław Wyspiański": (
        "playwright and painter",
        "1869–1907",
        "Born in Kraków; his stained glass fills the Franciscan Basilica, and his "
        "play The Wedding is set in Bronowice, now part of the city.",
    ),
    "Helena Modjeska": (
        "actress",
        "1840–1909",
        "Born in Kraków, where she began her stage career before moving to "
        "Warsaw and, in 1876, to the United States.",
    ),
    "Veit Stoss": (
        "sculptor of the St. Mary's altarpiece",
        "c. 1447–1533",
        "Spent some twenty years in Kraków, where he carved the great altarpiece "
        "of St. Mary's Basilica (1477–1489).",
    ),
    "Czesław Miłosz": (
        "poet, Nobel laureate",
        "1911–2004",
        "Spent his last years in Kraków and is buried in the Crypt of Merit at "
        "Skałka.",
    ),
    "Nicolaus Copernicus": (
        "astronomer",
        "1473–1543",
        "Studied at the University of Kraków — today's Jagiellonian University — "
        "from 1491 to about 1495.",
    ),
    "Tadeusz Kościuszko": (
        "military leader",
        "1746–1817",
        "Swore his oath on Kraków's Main Square in 1794, starting the Kościuszko "
        "Uprising; he is buried in Wawel Cathedral, and Kościuszko Mound honours "
        "him.",
    ),
    "Oskar Schindler": (
        "industrialist",
        "1908–1974",
        "Ran an enamel factory in Kraków's Zabłocie district, where he protected "
        "the Jewish workers he would save from the Holocaust.",
    ),
    "Helena Rubinstein": (
        "cosmetics entrepreneur",
        "1872–1965",
        "Born in Kazimierz, Kraków's Jewish quarter, before building her "
        "cosmetics empire abroad.",
    ),
    "Józef Piłsudski": (
        "statesman",
        "1867–1935",
        "His Polish Legions set out from Kraków in 1914; he is buried in Wawel "
        "Cathedral, and Piłsudski's Mound honours him.",
    ),
    "Bronisław Malinowski": (
        "anthropologist",
        "1884–1942",
        "Born in Kraków, he took his doctorate at the Jagiellonian University "
        "before pioneering anthropological fieldwork in London.",
    ),
}


class People(WikiImages, CategoryProvider):
    key = "people"
    items = list(PEOPLE)
    tag_style = "plain"

    def get_tag(self, item):
        role, years, _krakow = PEOPLE[item]
        return f"{role} · {years}"

    def get_details(self, item):
        """Their Kraków link first, then the Wikipedia intro."""
        krakow = PEOPLE[item][2]
        intro = (super().get_details(item) or {}).get("text")
        return {"text": f"{krakow}\n\n{intro}" if intro else krakow}


# --------------------------------------------------------------------------- #
# Green — the river, parks and green spaces of the city.                      #
# --------------------------------------------------------------------------- #


class Green(WikiImages, CategoryProvider):
    key = "geography:green"
    map_zoom = 15
    map_bounds = KRAKOW_BOUNDS
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


# For the details panel: how to say it (stress in capitals — in Polish it's
# almost always the second-to-last syllable) and when to use it.
PHRASE_NOTES = {
    "cześć": ("cheshch", "The everyday hi — and bye — among friends. With strangers, say dzień dobry."),
    "dzień dobry": ("jen DOB-ri", "The polite hello, used all day until the evening; it literally means \"good day\"."),
    "dobry wieczór": ("DOB-ri VYEH-choor", "The polite hello once evening comes."),
    "dobranoc": ("do-BRAH-nots", "Said when going to bed or leaving late at night — not as a greeting."),
    "do widzenia": ("do vee-DZEH-nya", "The polite goodbye; literally \"until seeing (you again)\"."),
    "do zobaczenia": ("do zo-ba-CHEH-nya", "A warmer goodbye when you'll meet again — \"see you\"."),
    "dziękuję": ("jen-KOO-yeh", "Thank you. Among friends, the shorter dzięki (JEN-kee) is fine."),
    "proszę": ("PRO-sheh", "Please — but also \"here you go\", \"you're welcome\" and \"pardon?\". You'll hear it everywhere."),
    "nie ma za co": ("nyeh ma ZA tso", "You're welcome; literally \"there's nothing (to thank) for\"."),
    "tak": ("tahk", "Yes. Often doubled, tak tak, as in \"yes, yes, I know\"."),
    "nie": ("nyeh", "No — and also \"not\": nie wiem, \"I don't know\"."),
    "przepraszam": ("psheh-PRAH-sham", "Sorry, and the way to say \"excuse me\" to get someone's attention or squeeze past."),
    "jak się masz?": ("yak sheh MASH", "How are you? — to friends. To a stranger, jak się pan/pani ma?"),
    "na zdrowie!": ("na ZDRO-vyeh", "Cheers! Literally \"to health\" — and also what you say when someone sneezes."),
    "nie rozumiem": ("nyeh ro-ZOO-myem", "I don't understand. Add proszę wolniej — \"slower, please\"."),
    "pomocy!": ("po-MO-tsi", "Help! Emergency number in Poland: 112."),
    "woda": ("VO-da", "Water. In a restaurant: gazowana (sparkling) or niegazowana (still)."),
    "piwo": ("PEE-vo", "Beer. Ordering: jedno piwo, proszę — \"one beer, please\"."),
    "przyjaciel": ("pshi-YA-chel", "A close friend (a woman is przyjaciółka); for a mate or colleague, kolega."),
    "miłość": ("MEE-woshch", "Love, the noun. \"I love you\" is kocham cię (KO-ham chyeh)."),
}


def _text_card(text):
    """Render a short phrase as an SVG data-URI to use as the card image."""
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


# The same phrases keyed by their Polish, for the Polish → English direction.
ENGLISH = {polish: english for english, polish in PHRASES.items()}

AUDIO_DIR = Path(__file__).resolve().parent.parent / "static" / "audio"
_AUDIO_EXTS = (".mp3", ".m4a", ".ogg", ".wav", ".webm", ".aac")


def phrase_slug(polish):
    """``"jak się masz?"`` -> ``"jak-sie-masz"`` (recording filename)."""
    folded = unicodedata.normalize("NFKD", polish.replace("ł", "l").replace("Ł", "L"))
    ascii_text = folded.encode("ascii", "ignore").decode().lower()
    return "-".join(re.findall(r"[a-z0-9]+", ascii_text))


class EnglishToPolish(CategoryProvider):
    """Read the English, say the Polish."""

    key = "language:english → polish"
    light_bg = True
    items = list(PHRASES)

    def polish(self, item):
        return PHRASES[item]

    def get_image(self, item):
        polish = self.polish(item)
        return {
            "name": polish,
            "image": _text_card(item),
            "url": f"https://en.wiktionary.org/wiki/{quote(polish)}",
        }

    def get_details(self, item):
        say, note = PHRASE_NOTES[self.polish(item)]
        return {"text": f"Say: {say}\n\n{note}"}

    def get_audio(self, item):
        """The Polish phrase, spoken: a native speaker's recording from
        static/audio/<slug>.<ext> when there is one, else the browser's voice."""
        polish = self.polish(item)
        slug = phrase_slug(polish)
        recording = next(
            (AUDIO_DIR / f"{slug}{ext}" for ext in _AUDIO_EXTS if (AUDIO_DIR / f"{slug}{ext}").exists()),
            None,
        )
        audio = {"text": polish, "lang": "pl-PL"}
        if recording:
            audio["src"] = f"/static/audio/{recording.name}"
        return audio


class PolishToEnglish(EnglishToPolish):
    """The other way round: read the Polish, name the English."""

    key = "language:polish → english"
    items = list(ENGLISH)

    def polish(self, item):
        return item

    def get_image(self, item):
        return {**super().get_image(item), "name": ENGLISH[item]}


# --------------------------------------------------------------------------- #
# Marta's tips — favourite places in Kazimierz and around the Rynek, mostly    #
# Marta's, each credited to whoever shared it (tag: area · tag · from who).    #
# The details panel carries their own words, a link to the area and a map      #
# pin; "know more" opens the venue's own page.                                 #
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
        "by": "Marta",
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
        "by": "Marta",
        "tag": "Jewish food",
        "text": "Jewish food in Kazimierz.",
        "link": "https://klezmer.pl/klezmer-hois/",
        "photo": "KRAKÓW, AB. 126.JPG",
        "pin": (50.0532169, 19.9482568, 17),
    },
    "Hevre": {
        "area": "Kazimierz",
        "by": "Marta",
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
        "by": "Marta",
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
        "by": "Marta",
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
        "by": "Marta",
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
    "Lokator": {
        "area": "Kazimierz",
        "by": "Marta",
        "tag": "bookshop for book lovers",
        "text": (
            "One more tip for book lovers :) A bookshop and publisher — they've "
            "got kids' books as well, and in English."
        ),
        "link": "https://lokatormedia.pl/",
        "photo": None,
        "pin": (50.0480823, 19.9453272, 17),
    },
    "Bunkier Cafe": {
        "area": "Rynek",
        "by": "Marta",
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
        "by": "Marta",
        "tag": "iconic bar & coffee shop",
        "text": "Another iconic bar / coffee shop.",
        "link": "https://karnet.krakowculture.pl/531-krakow-nowa-prowincja",
        "photo": "Nowa Prowincja Kraków.jpg",
        "pin": (50.0604258, 19.9361543, 17),
    },
    "Kino Pod Baranami": {
        "area": "Rynek",
        "by": "Marta",
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
    "Cytat Café": {
        "area": "Kazimierz",
        "by": "Cristina",
        "tag": "café full of books",
        "text": (
            "Cristina was recommended this one too: a café that's also a "
            "second-hand bookshop, with shelves and an archway made of books. "
            "They bake their own bread for breakfast."
        ),
        # Their own site (cytatcafe.pl) has an expired certificate.
        "link": (
            "https://www.google.com/maps/place/Cytat+Caf%C3%A9/@50.0526879,19.945034,17z/"
            "data=!4m6!3m5!1s0x47165b6af115a03b:0xb31bc17ebef0b863!8m2!3d50.0526879!4d19.945034"
        ),
        "photo": None,
        "pin": (50.0526879, 19.945034, 17),
    },
    "Black Duck": {
        "area": "Rynek",
        "by": "Cristina",
        "tag": "Polish restaurant",
        "text": (
            "Cristina was recommended this one: Czarna Kaczka, a Polish "
            "restaurant between the Rynek and Wawel. The house speciality is, "
            "as the name says, roast duck."
        ),
        "link": "https://czarnakaczka.pl/",
        "photo": "Restoracja Czarna Kaczka w Krakowie.jpg",
        "pin": (50.0582485, 19.9391763, 17),
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
        return f"{tip['area']} · {tip['tag']} · from {tip['by']}"

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
    EnglishToPolish(),
    PolishToEnglish(),
    MartasTips(),
]
for _provider in PROVIDERS:
    register(_provider)
