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
- **geography → districts** — 7 neighbourhoods, each shown as a locator map
  highlighting it on the city (Kazimierz, Podgórze, Nowa Huta…)
- **geography → green** — 6 green spaces and the river (Vistula, Błonia, the
  Botanical Garden, Kraków Zoo…)
- **people** — 9 famous cracovians, tagged with what they're known for
- **language** — 20 everyday phrases: read the English, reveal the Polish
  (the prompt is a rendered text card, not a photo)
- **marta's tips** — a local's battle-tested favourites in Kazimierz and
  around the Rynek (Hevre, Okrąglak, Bunkier Cafe, Kino Pod Baranami…); the
  tag carries Marta's note and *know more* opens the venue's own page.
  Venues have pinned Commons photos; drop a photo at
  `memi_kr/static/tips/<slug>.jpg` (e.g. `metal-wino.jpg`) to add or replace one

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
