# Core Web Vitals View Transition Test
This project is designed to measure the impact of view transitions on the Largest Contentful Paint (LCP) metric. It consists of several HTML pages with and without view transitions, and a JavaScript file to measure and store LCP timings.

You can view a live demo of the project [here](https://corewebvitals.github.io/view-transition/).

## Project Structure

- `index.html`: Entry point for the test without view transitions.
- `index-vt1.html` and `index-vt2.html`: Pages with view transitions enabled.
- `index-nvt1.html` and `index-nvt2.html`: Pages without view transitions.
- `results.html`: Displays the results of the LCP measurements.
- `lcp.js`: JavaScript file to measure and store LCP timings.

## How to Use

1. Open `index.html` in your browser to start the test.
2. Follow the navigation links to load pages with and without view transitions.
3. The LCP timings will be measured and stored in `localStorage`.
4. Once 100 LCP timings are collected, you will be redirected to `results.html` to view the average LCP timings for pages with and without view transitions.

## Measuring LCP

The `lcp.js` script measures the LCP timing for each page load and stores the timings in `localStorage`. The script also updates the footer with the latest LCP timing and the average LCP timing.

## Viewing Results

The `results.html` page calculates and displays the average LCP timings for the first 50 and the next 50 page loads. It also highlights the faster variant in green and the slower variant in red.

## Clearing Data

The `index.html` page clears the `localStorage` when loaded to ensure a fresh start for each test.

## Notes

- Ensure that your browser cache is disabled or emulate a slow device to simulate uncached page loads.
- The test requires at least 100 LCP timings to calculate and display the results.

## License

This project is licensed under the MIT License.
