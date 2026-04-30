window.addEventListener("load", () => {
  const images = document.querySelectorAll("img");
  let imagesLoaded = 0;

  images.forEach((img) => {
    if (img.complete) {
      imagesLoaded++;
    } else {
      img.addEventListener("load", () => {
        imagesLoaded++;
        if (imagesLoaded === images.length) {
          measure();
        }
      });
    }
  });

  if (imagesLoaded === images.length) {
    measure();
  }
});

const measure = () => {
  setTimeout(() => {
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lcpEntry = entries[entries.length - 1];
      console.log("LCP candidate:", lcpEntry);
      const lcpTiming = lcpEntry.startTime;

      // Get previous LCP timings from localStorage
      let lcpTimings = JSON.parse(localStorage.getItem("lcpTimings")) || [];
      lcpTimings.push(lcpTiming);

      // Save updated LCP timings to localStorage
      localStorage.setItem("lcpTimings", JSON.stringify(lcpTimings));

      // Calculate average LCP timing
      const totalLcp = lcpTimings.reduce((acc, curr) => acc + curr, 0);
      const averageLcp = totalLcp / lcpTimings.length;

      // Update the footer with the latest LCP timing and average LCP timing
      document.getElementById("lcp-timing").textContent = `LCP:  ${lcpTiming.toFixed(2)} ms | Avg: ${averageLcp.toFixed(2)} ms`;

      const navLinks = document.querySelectorAll("nav a");
      if (lcpTimings.length <= 50) {
        if (window.location.pathname.endsWith("index-vt2.html")) {
          navLinks[0].click();
        } else {
          navLinks[1].click();
        }
      } else if (lcpTimings.length <= 100) {
        if (window.location.pathname.endsWith("index-nvt2.html")) {
          navLinks[2].click();
        } else {
          navLinks[3].click();
        }
      } else {
        window.location.href = "results.html";
      }
    }).observe({ type: "largest-contentful-paint", buffered: true });
  }, 1000);
};
