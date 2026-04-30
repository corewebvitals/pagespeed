let timeinms = null;

document.addEventListener("DOMContentLoaded", () => {
  const images = document.querySelectorAll("img");
  const videos = document.querySelectorAll("video");
  const animatedElements = document.querySelectorAll(".animated");

  const mediaElements = [...images, ...videos];

  const loadMedia = (media) => {
    if (media.complete) {
      return Promise.resolve();
    }

    if (media.tagName.toLowerCase() === "video" && media.readyState == 4) {
      return Promise.resolve();
    }

    return new Promise((resolve) => {
      if (media.tagName.toLowerCase() === "img") {
        media.addEventListener("load", () => resolve());
      } else if (media.tagName.toLowerCase() === "video") {
        media.addEventListener("loadeddata", () => resolve());
      }
    });
  };

  const waitForAnimations = (element) => {
    return new Promise((resolve) => {
      const handleAnimationEnd = () => {
        element.removeEventListener("animationend", handleAnimationEnd);
        resolve();
      };
      element.addEventListener("animationend", handleAnimationEnd);
    });
  };

  Promise.all([
    ...mediaElements.map(loadMedia),
    ...[...animatedElements].map(waitForAnimations)
  ]).then(() => {
    logAndRedirect();
  });

  let progress = sessionStorage?.progress || 0;
  document.getElementById("progress").innerText = progress + '%';
});

setTimeout(() => {
  if (sessionStorage.testStarted) {
    window.location.reload();
  }
}, 50000);

new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    console.log("LCP candidate:", entry.startTime, entry);
    timeinms = entry.startTime.toFixed(0);
  }
}).observe({ type: "largest-contentful-paint", buffered: true });

const logAndRedirect = () => {
  console.log("Log and redirect");

  if (sessionStorage.testStarted) {
    setTimeout(() => {
      if (timeinms > 0) {
        console.log("LCP VALUE", timeinms);

        // save to session storage for the url, keep the last 50 values per url
        let url = window.location.href;

        let filename = url.substring(url.lastIndexOf("/") + 1);

        let lcpValues = sessionStorage.getItem(filename);
        if (lcpValues) {
          lcpValues = JSON.parse(lcpValues);
        } else {
          lcpValues = [];
        }
        lcpValues.push(timeinms);
        if (lcpValues.length > 50) {
          lcpValues.shift();
        }
        sessionStorage.setItem(filename, JSON.stringify(lcpValues));

        let avg = lcpValues.reduce((a, b) => parseInt(a) + parseInt(b), 0) / lcpValues.length;

        console.log("LCP VALUES", lcpValues);
      }

      // Example list of URLs with their entry counts
      const urls = Object.keys(sessionStorage)
        .filter((key) => {
          if (key == "testStarted" || key.startsWith("index.html") || key=='progress') {
            return false;
          }
          return true;
        })
        .map((key) => {
          return {
            url: key,
            entries: JSON.parse(sessionStorage.getItem(key)).length,
          };
        });

      // Filter URLs with less than sessionStorage.testStarted entries
      const filteredUrls = urls.filter((item) => item.entries < sessionStorage.testStarted);

      let totalentries = urls.reduce((a, b) => a + b.entries, 0);
      let progress = totalentries / (urls.length * sessionStorage.testStarted);
      sessionStorage.progress = Math.round(progress*100) ; 

      if (filteredUrls.length === 0) {
        sessionStorage.removeItem("testStarted");
        window.location.href = "index.html";
      } else {
        // Get a random URL from the filtered list
        const randomUrl = filteredUrls[Math.floor(Math.random() * filteredUrls.length)].url;

        window.location.href = randomUrl;
      }
    }, 400);
  }
};
