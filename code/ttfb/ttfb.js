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
    const workerStart = Math.max(pageNav.workerStart - activationStart, 0);
    const dnsStart = Math.max(pageNav.domainLookupStart - activationStart, 0);
    const tcpStart = Math.max(pageNav.connectStart - activationStart, 0);
    const sslStart = Math.max(pageNav.secureConnectionStart - activationStart, 0);
    const requestStart = Math.max(pageNav.requestStart - activationStart, 0);
    const responseStart = Math.max(pageNav.responseStart - activationStart, 0);

    // attribution based on https://www.w3.org/TR/navigation-timing-2/#processing-model
    const attribution = {
      redirectTime: formatTime(workerStart - activationStart),
      workerAndCacheTime: formatTime(dnsStart - workerStart),
      dnsTime: formatTime(tcpStart - dnsStart),
      tcpTime: formatTime(sslStart - tcpStart),
      sslTime: formatTime(requestStart - sslStart),
      requestTime: formatTime(responseStart - requestStart),
      totalTTFB: formatTime(responseStart - activationStart),
    };

    // log the results
    console.log('%cTime to First Byte ('+attribution.totalTTFB+'ms)', 'color: blue; font-weight: bold;');
    console.table(attribution);

    console.log('%cOrigininal navigation entry', 'color: blue; font-weight: bold;');
    console.log(pageNav);

  }).observe({
    type: 'navigation',
    buffered: true
  });
})();
