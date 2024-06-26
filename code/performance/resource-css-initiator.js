/* log all background images on a page to the console */
const imageExtensions = ['jpg', 'jpeg', 'png', 'webp', 'avif', 'jxl', 'gif', 'svg'];

let bgimg = performance.getEntriesByType('resource')
  .filter(rs => rs.initiatorType == 'css' && (rs?.contentType?.startsWith('image') || imageExtensions.includes(rs?.name?.split('.').pop().toLowerCase())))
  .map(rs => {
    return {
      name: rs.name,
      initiator: rs.initiatorType
    }
  }) || [];

(bgimg.length > 0) ?
  console.table(bgimg) :
  console.log('No background images on this page!');
