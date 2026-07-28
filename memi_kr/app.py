"""memi kraków — practise your memory of Kraków."""

import json

from flask import abort
from memi_engine import MemiConfig, create_app

import memi_kr.providers  # noqa: F401  (import registers the providers)
from memi_kr.providers.categories import PROVIDERS

# --------------------------------------------------------------------------- #
# Shareable category landing pages                                            #
#                                                                             #
# Each menu item gets a pretty, shareable URL (e.g. kr.memi.click/food) that  #
# opens the game with that category already selected and playing. The engine  #
# owns the whole frontend, so we add this without touching it:                #
#   * a slug route serves the normal index page at the pretty URL, and        #
#   * a small bootstrap script — injected through the one site-wide HTML hook #
#     the engine exposes (``analytics_html``) — reads the slug on load and     #
#     drives the existing menu exactly as a click would.                       #
# Slugs are derived from the registered category keys (the last ":"-segment),  #
# so new categories become shareable automatically.                            #
# --------------------------------------------------------------------------- #

CATEGORY_SLUGS: dict[str, str] = {}
for _p in PROVIDERS:
    _slug = _p.key.rsplit(":", 1)[-1]
    # Last-segment slugs are unique today; on a future collision fall back to
    # the full dashed key so both categories stay reachable.
    if _slug in CATEGORY_SLUGS:
        _slug = _p.key.replace(":", "-")
    CATEGORY_SLUGS[_slug] = _p.key

_LANDING_JS = """
<script>
(function () {
  var SLUGS = %s;
  function resolve() {
    var q = new URLSearchParams(location.search).get('cat');
    if (q) return q;
    var seg = location.pathname.replace(/^\\/+|\\/+$/g, '');
    return SLUGS[seg] || null;
  }
  var cat = resolve();
  if (!cat) return;
  function mainBtn(label) {
    return Array.prototype.slice
      .call(document.querySelectorAll('#main-categories button'))
      .find(function (b) { return b.textContent.trim() === label; });
  }
  var parts = cat.split(':');
  var top = mainBtn(parts[0]);
  if (!top) return;
  top.click();                       // top-level: selects & loads; parent: opens submenu
  if (parts.length > 1) {
    var sub = document.querySelector('#submenu-buttons [data-key="' + cat + '"]');
    if (sub) sub.click();            // pick the subcategory, which starts the game
  }
})();
</script>
""" % json.dumps(CATEGORY_SLUGS)

# --------------------------------------------------------------------------- #
# Analytics — GoatCounter (privacy-friendly, no cookies).                      #
# kr has its own GoatCounter site so its stats stay separate from the other    #
# memi games; the pretty landing paths (/food, /people, …) show up as their    #
# own pages in the dashboard.                                                   #
# --------------------------------------------------------------------------- #

GOATCOUNTER_CODE = "memi-kr"
_GOATCOUNTER_JS = (
    f'<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count"'
    ' async src="//gc.zgo.at/count.js"></script>\n'
)

config = MemiConfig(
    title="memi kraków",
    subtitle="name the sights, food and people of Kraków",
    wikipedia_lang="en",
    favicon_color="#2a5caa",
    sponsor_url="https://github.com/sponsors/filias",
    sponsor_text="sponsor",
    related_sites=[
        {"name": "memi", "url": "https://memi.click"},
        {"name": "memi portugal", "url": "https://pt.memi.click"},
        {"name": "memi lisboa", "url": "https://lx.memi.click"},
        {"name": "memi slovensko", "url": "https://sk.memi.click"},
        {"name": "memi US", "url": "https://us.memi.click"},
        {"name": "memi pyrenees", "url": "https://py.memi.click"},
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
    # Injected at the bottom of every page (after the engine's app.js loads):
    # GoatCounter analytics + the shareable-landing bootstrap.
    analytics_html=_GOATCOUNTER_JS + _LANDING_JS,
)

app = create_app(config)


@app.route("/<slug>")
def category_landing(slug):
    """Serve the game at a pretty, shareable per-category URL (e.g. /food).

    Renders the normal index page at the pretty URL — the injected bootstrap
    script reads the slug and opens the matching category. Unknown slugs 404;
    the engine's own routes (/about, /healthz, /favicon.svg, /static/…, /api/…)
    are more specific and still take precedence.
    """
    if slug not in CATEGORY_SLUGS:
        abort(404)
    return app.view_functions["index"]()


if __name__ == "__main__":
    app.run(debug=True, port=8091)
