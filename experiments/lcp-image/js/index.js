const startTest = async (n) => {
  return (
    confirm("Did you remember to disable the brower cache en select 4g network speed?") &&
    (() => {
      sessionStorage.clear();
      const listItems = document.querySelectorAll(".list-group-item a");
      listItems.forEach((item) => {
        const url = item.getAttribute("href");
        let filename = url.substring(url.lastIndexOf("/") + 1);
        sessionStorage.setItem(filename, JSON.stringify([]));
      });

      sessionStorage.setItem("testStarted", n);

      const listItemsArray = Array.from(listItems);
      const randomItem = listItemsArray[Math.floor(Math.random() * listItemsArray.length)];
      window.location.href = randomItem.getAttribute("href");
    })()
  );
};

const startSlowButton = document.getElementById("startSlowTest");
const startFastButton = document.getElementById("startFastTest");
startSlowButton && startSlowButton.addEventListener("click", () => startTest(50));
startFastButton && startFastButton.addEventListener("click", () => startTest(10));

window.addEventListener("load", function () {
  let data = [];

  const listItems = document.querySelectorAll(".list-group-item a");
  listItems.forEach((item) => {
    const url = item.getAttribute("href");
    const linkText = item.textContent;
    const arr = sessionStorage.getItem(url);

    const p75thvalue = arr ? JSON.parse(arr).sort((a, b) => a - b)[Math.floor(JSON.parse(arr).length * 0.75)] : 0;
    console.log(p75thvalue);

    data.push({ url, linkText, p75thvalue });

    if (p75thvalue) {
      /* add it to the badge aside the link*/
      const closestRow = item.closest(".row");
      const existingSpan = closestRow.querySelector(".badge");
      if (existingSpan) {
        existingSpan.textContent = `p75: ${p75thvalue}ms`;
      }
    }
  });

  // the default options for the chart
  const options = {
    layout: {
      padding: 40,
    },
    scales: {
      y: {
        beginAtZero: true,
        border: {
          display: false,
          dash: [5, 5],
        },
        grid: {
          color: "#ddd",
        },
        ticks: {
          callback: function (value) {
            if (value > 1000) {
              return (value / 1000).toFixed(2) + " s";
            }
            return value + " ms";
          },
        },
      },
      x: {
        border: {
          display: false,
        },
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 25,
          minRotation: 25,
          font: {
            size: 11,
            family: "Arial, sans-serif",
            weight: "bold",
            color: "#333",
          },
        },
      },
    },
  };

  // Create a container for the chart
  const chartContainer = document.getElementById("chartContainer");

  // Create the chart using Chart.js
  const canvas = document.createElement("canvas");
  chartContainer.appendChild(canvas);

  const ctx = canvas.getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.map((item) => item.linkText),
      datasets: [
        {
          label: "P75 LCP Timing (ms)",
          data: data.map((item) => item.p75thvalue),
          backgroundColor: "#0d6efd",
          borderColor: "#0d6efd",
          borderWidth: 1,
        },
      ],
    },
    options,
  });

  const chartContainerSorted = document.getElementById("chartContainersorted");

  // Create the chart using Chart.js
  const canvas2 = document.createElement("canvas");
  chartContainerSorted.appendChild(canvas2);

  const ctx2 = canvas2.getContext("2d");
  new Chart(ctx2, {
    type: "bar",
    data: {
      labels: data.sort((a, b) => a.p75thvalue - b.p75thvalue).map((item) => item.linkText),
      datasets: [
        {
          label: "P75 LCP Timing (ms)",
          data: data.sort((a, b) => a.p75thvalue - b.p75thvalue).map((item) => item.p75thvalue),
          backgroundColor: "#0d6efd",
          borderColor: "#0d6efd",
          borderWidth: 1,
        },
      ],
    },
    options,
  });
});
