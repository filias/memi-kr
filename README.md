# memi kraków

A memory card game about Kraków, built on
[memi-engine](https://github.com/filias/memi-engine).

Live at [kr.memi.click](https://kr.memi.click)

## Categories

- **landmarks** — 14 iconic sights (Wawel, St. Mary's, the Cloth Hall…)
- **churches** — 8 of Kraków's historic churches
- **museums** — 7 museums (Schindler's Factory's neighbours: Rynek Underground,
  Czartoryski, MOCAK, Manggha…)
- **districts** — 7 neighbourhoods (Kazimierz, Podgórze, Nowa Huta…)
- **food** — 10 Kraków and Polish classics (obwarzanek, zapiekanka, pierogi…)
- **people** — 10 famous cracovians, tagged with what they're known for
- **nearby** — 7 classic day trips (Wieliczka, Zakopane, Jasna Góra…)

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
