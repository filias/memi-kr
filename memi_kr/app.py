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

# --------------------------------------------------------------------------- #
# "know more" — the engine renders it as small grey text in the row under the  #
# card, which on a phone falls below the fold (the card fills the width). Make #
# it an accent pill, and on phones pin it to the bottom of the screen while    #
# it's showing (the engine toggles its inline display on reveal). The engine   #
# has no custom-CSS hook, so this rides along in analytics_html.               #
# --------------------------------------------------------------------------- #

_KNOW_MORE_CSS = """<style>
.more-link {
    padding: 0.35rem 1rem;
    border: 2px solid var(--accent);
    border-radius: 2rem;
    color: var(--accent);
    font-weight: 600;
}
.more-link:hover { background: var(--accent); color: var(--bg); }
@media (max-width: 600px) {
    .more-link {
        position: fixed;
        left: 50%;
        bottom: calc(1rem + env(safe-area-inset-bottom));
        transform: translateX(-50%);
        z-index: 50;
        padding: 0.75rem 1.75rem;
        background: var(--accent);
        color: var(--bg);
        font-size: 1rem;
        white-space: nowrap;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    body { padding-bottom: 5rem; }
}
</style>"""

config = MemiConfig(
    title="memi kraków",
    subtitle="name the sights, food and people of Kraków",
    wikipedia_lang="en",
    favicon_color="#2a5caa",
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
        royal capital. Landmarks, churches, districts, food and famous
        cracovians &mdash; there's always something to remember.</p>

        <h2>How to play</h2>
        <p>Pick a category, look at the image, and try to name it before
        revealing the answer. No accounts, no scores, no time limits.</p>
        <ul>
            <li><strong>clues:</strong> toggle progressive letter hints.</li>
            <li><strong>know more:</strong> appears on reveal and opens the
            Wikipedia article for the item.</li>
            <li><strong>report:</strong> flag a card if the image doesn't match
            the answer.</li>
        </ul>

        <h2>Why it works</h2>
        <p>This is a simple form of <em>active recall</em> &mdash; pulling a
        name out of memory instead of re-reading it. Retrieval practice builds
        more durable memory than re-exposure alone, and because each prompt is a
        picture it also leans on the <em>picture superiority effect</em>.</p>
    """,
    # Injected at the bottom of every page (after the engine's app.js loads).
    analytics_html=_KNOW_MORE_CSS + _GOATCOUNTER_JS,
)

# static/ holds photos for cards with no usable Commons image (Marta's tips).
app = create_app(config, instance_static=str(Path(__file__).parent / "static"))

if __name__ == "__main__":
    app.run(debug=True, port=8091)
