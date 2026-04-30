# pagespeed

Hub for Core Web Vitals experiments and code samples.
Live at **https://corewebvitals.github.io/pagespeed/**.

For more about the Core Web Vitals check out [corewebvitals.io](https://www.corewebvitals.io).

## Layout

```
experiments/   ← interactive HTML demos (open in a browser)
code/          ← drop-in code samples grouped by metric
```

## Experiments

Visit each one in the browser at the live URL.

| Folder | Live | About |
|---|---|---|
| [`experiments/michotte-inp`](experiments/michotte-inp) ★ | [▶ demo](https://corewebvitals.github.io/pagespeed/experiments/michotte-inp/) | The 1946 Michotte launching-effect experiment whose 100/200ms causality thresholds became the modern INP buckets — interactive replication |
| [`experiments/lcp-image`](experiments/lcp-image) | [▶ demo](https://corewebvitals.github.io/pagespeed/experiments/lcp-image/) | ~25 variants of an LCP image (lazy, preload, fetchpriority, AVIF/WebP, picture, video poster, …) |
| [`experiments/view-transition`](experiments/view-transition) | [▶ demo](https://corewebvitals.github.io/pagespeed/experiments/view-transition/) | Measure how `view-transition-name: auto` affects LCP across navigations |
| [`experiments/datalayer-schedule-after-paint`](experiments/datalayer-schedule-after-paint) | [▶ demo](https://corewebvitals.github.io/pagespeed/experiments/datalayer-schedule-after-paint/demo.html) | Drop-in script that defers `dataLayer.push` until after paint to protect INP |

## Code samples

Snippets you can copy into your own site, grouped by Core Web Vital.

| Folder | About |
|---|---|
| [`code/cls`](code/cls) | Cumulative Layout Shift fixes |
| [`code/inp`](code/inp) | Interaction to Next Paint patterns |
| [`code/performance`](code/performance) | General performance helpers |
| [`code/ttfb`](code/ttfb) | Time to First Byte |

## History

This repo absorbed three previously-separate experiment repos in 2026-04:

- `corewebvitals/lcp-image` → `experiments/lcp-image/`
- `corewebvitals/view-transition` → `experiments/view-transition/`
- `corewebvitals/DataLayer-schedule-after-paint` → `experiments/datalayer-schedule-after-paint/`

Those repos are archived and redirect to their new home.
