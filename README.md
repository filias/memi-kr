# memi kraków

A memory card game about Kraków, built on
[memi-engine](https://github.com/filias/memi-engine).

Live at [kr.memi.click](https://kr.memi.click)

## Categories

- **culture → sights** — 29 landmarks, churches and museums (Wawel, St. Mary's,
  the Cloth Hall, Rynek Underground, MOCAK…)
- **culture → food** — 10 Kraków and Polish classics (obwarzanek, zapiekanka, pierogi…)
- **geography → districts** — 7 neighbourhoods, each shown as a locator map
  highlighting it on the city (Kazimierz, Podgórze, Nowa Huta…)
- **people** — 9 famous cracovians, tagged with what they're known for

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
