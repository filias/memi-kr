# memi kraków

A memory card game about Kraków, built on
[memi-engine](https://github.com/filias/memi-engine).

Live at [kr.memi.click](https://kr.memi.click)

## Categories

- **culture → sights** — 38 landmarks, churches, museums, mounds and the
  Kazimierz synagogues, each tagged with its date (Wawel, St. Mary's, MOCAK…)
- **culture → food** — 10 Kraków and Polish classics (obwarzanek, zapiekanka, pierogi…)
- **culture → folklore** — 5 legends and folk traditions (the Wawel Dragon,
  Pan Twardowski, Lajkonik, the szopka, the Sigismund Bell)
- **geography → districts** — 12 neighbourhoods (Kazimierz, Podgórze, Nowa
  Huta, Tyniec, Łagiewniki…), each a photo of the place with a locator-map
  inset zoomed around it. The cards are prebuilt by
  `uv run --with pillow python scripts/build_district_cards.py` into
  `memi_kr/static/districts/` (credits in `CREDITS.md` there)
- **geography → green** — 6 green spaces and the river (Vistula, Błonia, the
  Botanical Garden, Kraków Zoo…)
- **people** — 15 famous cracovians, tagged with what they're known for; the
  details panel opens with their link to Kraków
- **language** — 21 everyday phrases, in two directions: *polish → english*
  (read the Polish, reveal the English; what the submenu opens on) and
  *english → polish* (the other way round); the submenu's *all* chip mixes
  both. The prompt is a rendered text card, not a photo, and the old
  `/language` link opens polish → english. A speaker button says the
  Polish — on reveal, or straight away in polish → english, so you can hear
  it before answering: a native speaker's recording from
  `memi_kr/static/audio/` when there is one, else the browser's Polish voice.
  Import recordings (named after their phrase, e.g. `dziękuję.m4a`) with
  `uv run python scripts/import_audio.py <files>`
- **marta’s tips** — a local's battle-tested favourites in Kazimierz and
  around the Rynek (Hevre, Okrąglak, Bunkier Cafe, Kino Pod Baranami…), plus
  tips from other colleagues; each card says who it's from (`by` in `TIPS`).
  On reveal, a details panel shows the tip's own note, a link to the area and a
  map pin; *know more* opens the venue's own page. Venues have pinned Commons
  photos; drop a photo at `memi_kr/static/tips/<slug>.<ext>` (e.g.
  `metal-wino.jpg`) to add or replace one

The game uses the engine's **enriched** layout (`layout="enriched"`): the
details panel beside the card and a prominent *know more* button, pinned to
the bottom of the screen on phones. Every card except language fills the
panel from its Wikipedia article: the opening paragraph (pronunciation asides
stripped, trimmed to whole sentences) and, for places, a map pin from the
article's Wikidata coordinates (dropped when they fall outside Kraków, like the
Vistula's mouth on the Baltic).

Images and *know more* links resolve from Wikipedia automatically. A small
`WikiImages` mixin relaxes the engine's strict title lookup — following
redirects and falling back to search — so natural display names land on the
right article.

## Setup

```bash
uv sync
uv run python -m memi_kr.app      # dev server on http://localhost:8091
```

## Deploy

Same push-to-deploy flow as the other memi games: merging to `main` triggers a
GitHub webhook that pulls, `uv sync`s and restarts the service. See
[`deploy/`](deploy/).

## License

MIT
