(() => {

  const formatTime = (time) => {
    //round by 2 decimals, use Math.round() for integer
    return Math.round(time * 100) / 100;
  };

  new PerformanceObserver((entryList) => {
    const [pageNav] = entryList.getEntriesByType('navigation');

    // timing start times are relative
    const activationStart = pageNav.activationStart || 0;
    const waitEnd = Math.max((pageNav.workerStart || pageNav.fetchStart) - activationStart, 0);
    const dnsStart = Math.max(pageNav.domainLookupStart - activationStart, 0);
    const tcpStart = Math.max(pageNav.connectStart - activationStart, 0);
    const sslStart = Math.max(pageNav.secureConnectionStart - activationStart, 0);
    const tcpEnd = Math.max(pageNav.connectEnd - activationStart, 0);
    const responseStart = Math.max(pageNav.responseStart - activationStart, 0);

    // attribution based on https://www.w3.org/TR/navigation-timing-2/#processing-model
    // use associative array to log the results more readable
    let attributionArray = [];
    attributionArray['Redirect and Waiting duration'] = {'time in ms':formatTime(waitEnd)};
    attributionArray['Worker and Cache duration'] = {'time in ms':formatTime(dnsStart - waitEnd)};
    attributionArray['DNS duration'] = {'time in ms':formatTime(tcpStart - dnsStart)};
    attributionArray['TCP duration'] = {'time in ms':formatTime(sslStart - tcpStart)};
    attributionArray['SSL duration'] = {'time in ms':formatTime(tcpEnd - sslStart)};
    attributionArray['Request duration'] = {'time in ms':formatTime(responseStart - tcpEnd)};
    attributionArray['Total TTFB'] = {'time in ms':formatTime(responseStart)};

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
