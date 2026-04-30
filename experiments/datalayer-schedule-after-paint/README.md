# INP Yield Pattern for `dataLayer.push`

This script defers `dataLayer.push` calls in Google Tag Manager until after the next browser paint. The pattern helps prevent long input delay (INP) regressions caused by synchronous `push` operations during user interaction.

## Why this matters

Calling `dataLayer.push` synchronously during interaction can block rendering and increase interaction latency. By yielding execution until after the next paint, this script ensures updates happen at a safer point in the event loop.

## How it works

- The `awaitPaint` helper pauses execution until after the next animation frame and a small buffer delay.
- It falls back to a 200ms timeout in case `requestAnimationFrame` never fires.
- It wraps `window.dataLayer.push`, deferring all calls without changing existing GTM behavior.

## Usage

Add the contents of this script AFTER your GTM tag
