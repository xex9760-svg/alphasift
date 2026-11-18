# AlphaSift track record

Every trading day after the close, a GitHub Action runs each built-in strategy with `--no-llm --save-run` and commits the saved run here. Picks are never edited afterwards; the git history is the timestamped record. Each pick is then measured at T+5 / T+10 / T+20 trading days against its market benchmark.

**Dashboard:** https://zhulinsen.github.io/alphasift/ · Code: [ZhuLinsen/alphasift](https://github.com/ZhuLinsen/alphasift) · Updated 2026-11-18T07:11:25+00:00 · 2 saved runs

> For research only, not investment advice. Returns are close-to-close after a round-trip cost, ignore dividends, and small samples are noisy.

## Scorecard (T+5 / T+20)

| Market | Strategy | Runs | T+5 n | T+5 excess | T+5 beat | T+20 n | T+20 excess | T+20 beat |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| us | 全球低估值 | 1 | 0 | – | – | 0 | – | – |
| us | US Momentum Quality | 1 | 0 | – | – | 0 | – | – |

## Latest session

- **us** finished 2026-11-18T07:11:22+00:00: 2/2 strategies ok

Raw runs: [`data/runs/`](data/runs) · derived site data: [`site/`](site)
