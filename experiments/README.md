# Experiments

Interactive Core Web Vitals demos. Each subfolder is a self-contained experiment with its own README.

| Folder | Live | Focus |
|---|---|---|
| [`michotte-inp`](michotte-inp) ★ | [▶](https://corewebvitals.github.io/pagespeed/experiments/michotte-inp/) | INP — replicate the 1946 launching-effect experiment whose 100/200ms thresholds became the INP buckets |
| [`lcp-image`](lcp-image) | [▶](https://corewebvitals.github.io/pagespeed/experiments/lcp-image/) | LCP — image loading techniques |
| [`view-transition`](view-transition) | [▶](https://corewebvitals.github.io/pagespeed/experiments/view-transition/) | LCP — view transitions impact |
| [`datalayer-schedule-after-paint`](datalayer-schedule-after-paint) | [▶](https://corewebvitals.github.io/pagespeed/experiments/datalayer-schedule-after-paint/demo.html) | INP — defer `dataLayer.push` until after paint |

## Adding a new experiment

1. `mkdir experiments/<name>/`
2. Drop in `index.html` (or whatever entry point makes sense) and a `README.md`.
3. Link it from this index and from the top-level `index.html` and `README.md`.
