# The 1946 experiment that defined the INP threshold

An interactive demonstration of Albert Michotte's launching effect, and how his 1946 perceptual psychology research became the Interaction to Next Paint thresholds in Google's Core Web Vitals 80 years later.

**Live demo:** https://corewebvitals.github.io/pagespeed/experiments/michotte-inp/

## What this is

In 1946, Belgian psychologist Albert Michotte ran an experiment on how humans perceive causality. He showed people two moving shapes on a screen. Object A moves toward Object B. The moment they touch, A stops and B starts moving. Michotte varied the delay between contact and B's movement.

His finding:

- Below 100ms, people saw A causing B to move
- Between 100 and 200ms, perception was mixed
- Above 200ms, people saw two unrelated events

Those three buckets are the INP thresholds. This page lets you reproduce the experiment with a slider.

## The citation chain

1. **Michotte (1946).** *La perception de la causalité.* The original launching effect experiments.
2. **Miller (1968).** Response time in man-computer conversational transactions. Cited Michotte. Defined a 100ms threshold for "response to control activation."
3. **Nielsen (1993).** Response Times: The 3 Important Limits. Cited Miller. Established the 100ms / 1s / 10s framework that shaped a generation of HCI guidelines.
4. **Kaaresoja et al. (2014).** Towards the Temporally Perfect Virtual Button. Replicated the finding for touchscreens specifically.
5. **Google Chrome team (2022).** Defining Core Web Vitals thresholds. Cited the same research chain. Settled on 200ms as the "good" INP threshold because field data showed 100ms was unachievable on lower-end mobile devices.

Full sources are listed on the page.

## How it works

Single static HTML file. No build step, no dependencies, no tracking. Vanilla CSS and JavaScript. The interactive piece is a `requestAnimationFrame` loop driving two SVG rectangles, with a `setTimeout` for the variable delay between them.

The whole experiment is one file: `index.html`.

## Running locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000.

## License

MIT for the code in this folder. The historical and scientific content is paraphrased from the cited sources.

## Built by

[Arjen Karel](https://www.corewebvitals.io), independent Core Web Vitals consultant.
