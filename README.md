# LCP Test

This project is designed to test and improve the Largest Contentful Paint (LCP) metric by experimenting with different image loading techniques. For more information visit [Core Web Vitals - Optimize LCP Image](https://www.corewebvitals.io/core-web-vitals/largest-contentful-paint/optimize-lcp-image)

## Description

The project includes multiple versions of a simple HTML page, each with different image loading strategies:
- Normal image loading
- Lazy loading
- Preloading
- Resized images
- Converted images (WebP, AVIF, Picture tag)

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/corewebvitals/lcp-image.git
    cd lcp-test
    ```

2. Upload the files to a simple webserver. Self hosting this project on localhost will not mimic real world results


## Usage

1. Open `index.html` in your browser.
2. Click on the different versions of the HTML pages listed to see how each technique affects the LCP metric.
3. The average LCP value for each version is stored in the session storage and displayed next to the corresponding link.

## Automated test

1. First upload all the files to your webserver
2. Open the developer tools (F12) and go to the network tab
3. Disable your browsers cache by checking the disable cache checkbox
4. Keep the network tab open!! If you close it you you will just test your broser cache
5. Click on the start test button

## File Structure

- `index.html`: Main page listing all versions.
- `css/`: Directory containing CSS files.
- `js/`: Directory containing JavaScript files.
- `images/`: Directory containing images used in the tests.

## Additional Information

- The project loads Bootstrap CSS and JS to more closely mimic real world sites.
- Chart.js is used to visualize the LCP metrics.

## License

This project is licensed under the MIT License.