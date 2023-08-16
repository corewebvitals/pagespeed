/* dont really like the entries yet. This should make more sense!*/



let loafs = [];
function processAndFilterLoAFs(entries) {
  function floorObject(o) {
    return Object.fromEntries(Array.from(Object.entries(o)).map(([key, value]) =>
      [key, typeof value === "number" ? Math.floor(value) :
        value]))
  }

  function processEntry(entry) {

    const startTime = entry.startTime;
    const endTime = entry.startTime + entry.duration;
    const delay = entry.desiredRenderStart ? Math.max(0, entry.startTime - entry.desiredRenderStart) : 0;
    const deferredDuration = Math.max(0, entry.desiredRenderStart - entry.startTime);
    const renderDuration = entry.styleAndLayoutStart - entry.renderStart;
    const workDuration = entry.renderStart ? entry.renderStart - entry.startTime : entry.duration;
    const totalForcedStyleAndLayoutDuration = entry.scripts.reduce((sum, script) => sum + script.forcedStyleAndLayoutDuration, 0);
    const styleAndLayoutDuration = entry.styleAndLayoutStart ? endTime - entry.styleAndLayoutStart : 0;
    const scripts = entry.scripts.map(script => {
      const delay = script.startTime - script.desiredExecutionStart;
      const scriptEnd = script.startTime + script.duration;
      const compileDuration = script.executionStart - script.startTime;
      const execDuration = scriptEnd - script.executionStart;
      return floorObject({ delay, compileDuration, execDuration, ...script.toJSON() });
    })
    return floorObject({ startTime, delay, deferredDuration, renderDuration, workDuration, styleAndLayoutDuration, totalForcedStyleAndLayoutDuration, entry, scripts });
  }

  return entries.map(processEntry);
}

function perfObserver(list, observer) {
  loafs = [...loafs, ...processAndFilterLoAFs(list.getEntries())];
  console.log(loafs);

}
const observer = new PerformanceObserver(perfObserver);
observer.observe({ type: "long-animation-frame", buffered: true })
