/* log all background images on a page to the console */
let bgimg = performance.getEntriesByType('resource')
  .filter(rs => rs.initiatorType == 'css')
  .map(rs => {
  return {
    name: rs.name,
    initiator: rs.initiatorType
  }
}) || [];

(bgimg.length > 0)?
    console.table(bgimg):
    console.log('No background images on this page!');
