/**
 * Time to First Byte (TTFB) is a measurement used as an indication of the responsiveness of a webserver or other network resource. 
 * TTFB measures the duration from the user or client making an HTTP request to the first byte of the page being received by the client's browser.
 */

(() => {

  const formatTime = (time) => {
    //round by 2 decimals, use Math.round() for integer
    return Math.round(time * 100) / 100;

  };

  new PerformanceObserver((entryList) => {
    const [pageNav] = entryList.getEntriesByType('navigation');

    // timing start times are relative to navigationStart
    const activationStart = pageNav.activationStart || 0;
    const workerStart = Math.max(pageNav.workerStart - activationStart, activationStart);
    const dnsStart = Math.max(pageNav.domainLookupStart - activationStart, workerStart);
    const tcpStart = Math.max(pageNav.connectStart - activationStart, dnsStart);
    const sslStart = Math.max(pageNav.secureConnectionStart - activationStart, tcpStart);
    const requestStart = Math.max(pageNav.requestStart - activationStart, sslStart);
    const responseStart = Math.max(pageNav.responseStart - activationStart, requestStart);

    // attribution based on https://www.w3.org/TR/navigation-timing-2/#processing-model
    // use assosictive array to log the results more readable
    let attributionArray = [];
    attributionArray['Redirect Time'] = {'time in ms':formatTime(workerStart - activationStart)};
    attributionArray['Worker and Cache Time'] = {'time in ms':formatTime(dnsStart - workerStart)};
    attributionArray['DNS Time'] = {'time in ms':formatTime(tcpStart - dnsStart)};
    attributionArray['TCP Time'] = {'time in ms':formatTime(sslStart - tcpStart)};
    attributionArray['SSL Time'] = {'time in ms':formatTime(requestStart - sslStart)};
    attributionArray['Request Time'] = {'time in ms':formatTime(responseStart - requestStart)};
    attributionArray['Total TTFB'] = {'time in ms':formatTime(responseStart - activationStart)};

    // log the results
    console.log('%cTime to First Byte ('+formatTime(responseStart - activationStart)+'ms)', 'color: blue; font-weight: bold;');
    console.table(attributionArray);

    console.log('%cOrigininal navigation entry', 'color: blue; font-weight: bold;');
    console.log(pageNav);

  }).observe({
    type: 'navigation',
    buffered: true
  });
})();
