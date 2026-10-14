"""Build the district cards: a photo with a zoomed locator-map inset.

    uv run --with pillow python scripts/build_district_cards.py

For each entry in ``DISTRICTS`` this downloads the Commons photo and the SIM
locator map, finds the highlighted (red) district on the map, crops a square
around it with enough of the city to place it, and sets that into the photo's
top-right corner. Output: ``memi_kr/static/districts/<slug>.jpg`` plus
``CREDITS.md`` (the photos and maps are CC-licensed; the composites are
derivative works and carry the same attribution).

Rerun after changing a photo or adding a district; the images are committed.
"""

import io
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from memi_kr.providers.categories import DISTRICTS, DISTRICTS_DIR, district_slug  # noqa: E402

UA = {"User-Agent": "memi-krakow (+https://kr.memi.games)"}
API = "https://commons.wikimedia.org/w/api.php"
WIDTH = 1200  # output width
INSET = 0.34  # inset side, as a share of the output width
BG = (245, 243, 239)  # the site's light background, behind the map's transparency


def commons(filename, width):
    """Download a Commons file rendered at ``width`` px, with its credit line."""
    r = requests.get(
        API,
        params={
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": width,
            "titles": "File:" + filename,
        },
        headers=UA,
        timeout=30,
    ).json()
    info = next(iter(r["query"]["pages"].values()))["imageinfo"][0]
    meta = info["extmetadata"]
    artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "?"))
    credit = {
        "file": filename,
        "page": info["descriptionurl"],
        "artist": " ".join(artist.split()),
        "license": meta.get("LicenseShortName", {}).get("value", "?"),
    }
    image = Image.open(io.BytesIO(requests.get(info["thumburl"], headers=UA, timeout=60).content))
    return image, credit


def district_crop(locator):
    """Square crop of the locator map around its red district, on the site bg."""
    rgba = locator.convert("RGBA")
    flat = Image.new("RGB", rgba.size, BG)
    flat.paste(rgba, mask=rgba.getchannel("A"))
    r, g, b, a = rgba.split()
    # The district is the saturated red; the rest of the city is pale pink.
    red = ImageChops.multiply(
        r.point(lambda v: 255 if v > 150 else 0),
        ImageChops.multiply(g.point(lambda v: 255 if v < 90 else 0), b.point(lambda v: 255 if v < 90 else 0)),
    )
    box = red.getbbox()
    if box is None:
        raise ValueError("no highlighted district found on the map")
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    # Enough of the city around it to place it: 4x the district, but never so
    # tight that the river and neighbours drop out, nor wider than the map.
    side = max(4 * max(box[2] - box[0], box[3] - box[1]), 0.32 * flat.width)
    side = min(side, flat.width, flat.height)
    left = min(max(cx - side / 2, 0), flat.width - side)
    top = min(max(cy - side / 2, 0), flat.height - side)
    return flat.crop((round(left), round(top), round(left + side), round(top + side)))


def compose(photo, crop):
    photo = photo.convert("RGB")
    photo = photo.resize((WIDTH, round(photo.height * WIDTH / photo.width)), Image.LANCZOS)
    # A share of the width, but never most of a wide, short photo.
    side = round(min(WIDTH * INSET, photo.height * 0.55))
    inset = crop.resize((side, side), Image.LANCZOS)
    radius, border, margin = side // 12, 6, round(WIDTH * 0.03)

    # White rounded frame with a soft shadow, so the map reads on any photo.
    framed = Image.new("RGB", (side + 2 * border, side + 2 * border), "white")
    framed.paste(inset, (border, border))
    mask = Image.new("L", framed.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, *framed.size], radius=radius, fill=255)
    x, y = photo.width - framed.width - margin, margin
    shadow = Image.new("L", photo.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x + 4, y + 8, x + framed.width + 4, y + framed.height + 8], radius=radius, fill=110
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    photo = Image.composite(Image.new("RGB", photo.size, "black"), photo, shadow)
    photo.paste(framed, (x, y), mask)
    return photo


def main():
    DISTRICTS_DIR.mkdir(parents=True, exist_ok=True)
    credits = []
    for name, district in DISTRICTS.items():
        photo, photo_credit = commons(district["photo"], WIDTH)
        locator, map_credit = commons(f"Obszar SIM Krakowa – {district['area']}.svg", 1600)
        out = DISTRICTS_DIR / f"{district_slug(name)}.jpg"
        compose(photo, district_crop(locator)).save(out, quality=82, optimize=True, progressive=True)
        credits.append((name, out.name, photo_credit, map_credit))
        print(f"{name:12} -> {out.name} ({out.stat().st_size // 1024} KB)")
        time.sleep(0.5)

    lines = [
        "# District card credits",
        "",
        "Each card combines a photo with a crop of a locator map, both from",
        "Wikimedia Commons, built by `scripts/build_district_cards.py`. The",
        "combined images are shared under the same licences as their sources.",
        "",
    ]
    for name, filename, photo, locator in credits:
        lines += [
            f"## {name} (`{filename}`)",
            "",
            f"- Photo: [{photo['file']}]({photo['page']}) by {photo['artist']}, {photo['license']}",
            f"- Map: [{locator['file']}]({locator['page']}) by {locator['artist']}, {locator['license']}",
            "",
        ]
    (DISTRICTS_DIR / "CREDITS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
