"""memi kraków — practise your memory of Kraków."""

from pathlib import Path

from memi_engine import MemiConfig, create_app

import memi_kr.providers  # noqa: F401  (import registers the providers)

# --------------------------------------------------------------------------- #
# Analytics — GoatCounter (privacy-friendly, no cookies).                      #
# kr has its own GoatCounter site so its stats stay separate from the other    #
# memi games. Shareable per-category landing pages (/food, /people, …) are now #
# provided by the engine, so they show up as their own pages in the dashboard. #
# --------------------------------------------------------------------------- #

GOATCOUNTER_CODE = "memi-kr"
_GOATCOUNTER_JS = (
    f'<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count"'
    ' async src="//gc.zgo.at/count.js"></script>'
)

config = MemiConfig(
    title="memi kraków",
    # Details panel beside the card (Marta's notes + map) and a prominent
    # "know more" button, pinned to the bottom of the screen on phones.
    layout="enriched",
    subtitle="name the sights, food and people of Kraków",
    wikipedia_lang="en",
    favicon_color="#2a5caa",
    # Link-preview image for Slack, WhatsApp, etc. (1200×630, static/og.png).
    og_image="https://kr.memi.games/static/og.png",
    sponsor_url="https://github.com/sponsors/filias",
    sponsor_text="sponsor",
    related_sites=[
        {"name": "memi", "url": "https://world.memi.games"},
        {"name": "memi portugal", "url": "https://pt.memi.games"},
        {"name": "memi lisboa", "url": "https://lx.memi.games"},
        {"name": "memi slovensko", "url": "https://sk.memi.games"},
        {"name": "memi united states", "url": "https://us.memi.games"},
        {"name": "memi pyrenees", "url": "https://py.memi.games"},
    ],
    about_html="""
        <p>memi kraków is a memory practice game about Kraków, Poland's old
        royal capital: its sights, districts, food, legends, famous cracovians
        and everyday Polish &mdash; plus Marta's favourite places.</p>

        <h2>What's inside</h2>
        <ul>
            <li><strong>culture:</strong> landmarks, churches, museums and
            synagogues with their dates, Kraków food, and the city's legends.</li>
            <li><strong>geography:</strong> districts, each a photo with a small
            map of where it is, and the city's parks and green spaces.</li>
            <li><strong>people:</strong> famous cracovians and what ties them to
            the city.</li>
            <li><strong>language:</strong> everyday phrases &mdash; read the
            English, say the Polish, then listen to how it sounds.</li>
            <li><strong>marta&rsquo;s tips:</strong> battle-tested cafés, bars,
            food and a cinema in Kazimierz and around the Rynek, from
            Marta.</li>
        </ul>

        <h2>How to play</h2>
        <p>Pick a category, look at the image, and try to name it before
        revealing the answer. No accounts, no scores, no time limits.</p>
        <ul>
            <li><strong>clues:</strong> toggle progressive letter hints.</li>
            <li><strong>on reveal:</strong> a panel beside the card (below it on
            phones) tells you more and pins the place on a map.</li>
            <li><strong>listen:</strong> on language cards, the speaker button
            says the Polish out loud.</li>
            <li><strong>know more:</strong> opens the Wikipedia article &mdash;
            or, for Marta's tips, the place's own page.</li>
            <li><strong>share:</strong> the address bar always holds a link to
            the category you're playing, e.g.
            <a href="/martas-tips">kr.memi.games/martas-tips</a>.</li>
            <li><strong>report:</strong> flag a card if the image doesn't match
            the answer.</li>
        </ul>

        <h2>Why it works</h2>
        <p>This is a simple form of <em>active recall</em> &mdash; pulling a
        name out of memory instead of re-reading it. Retrieval practice builds
        more durable memory than re-exposure alone, and because each prompt is a
        picture it also leans on the <em>picture superiority effect</em>.</p>

        <h2>Credits</h2>
        <p>Photos from <a href="https://commons.wikimedia.org/">Wikimedia
        Commons</a> and descriptions from
        <a href="https://www.wikipedia.org/">Wikipedia</a>, under their
        Creative Commons licences (district photo credits are listed
        <a href="https://github.com/filias/memi-kr/blob/main/memi_kr/static/districts/CREDITS.md">here</a>).
        Maps &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>
        contributors. Tips by Marta.</p>
    """,
    # Injected at the bottom of every page (after the engine's app.js loads).
    analytics_html=_GOATCOUNTER_JS,
)

# static/ holds photos for cards with no usable Commons image (Marta's tips).
app = create_app(config, instance_static=str(Path(__file__).parent / "static"))

if __name__ == "__main__":
    app.run(debug=True, port=8091)
