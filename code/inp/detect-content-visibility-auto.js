/**
 * This snippet will output all the elements that have a content-visibility applied to them.
 * 
 * To test for content-visibility, we check the computed style of the element and see if it has a transition property.
 * 
 * Applying content-visibility to offscreen element can inporive the INP. The use a RUM tool like Core/Dash (https://coredash.app) to see how much content-visibility improves the INP.
 */

(() => {

  // Create an object to store the results
  let ret = {
    autoTable: [],
    autoNodeArray: []
  };


  // Get the name of the node
  function getName(node) {
    const name = node.nodeName;
    return node.nodeType === 1
      ? name.toLowerCase()
      : name.toUpperCase().replace(/^#/, '');
  }

  // Get the selector
  const getSelector = (node) => {
    let sel = '';

    try {
      while (node && node.nodeType !== 9) {
        const el = node;
        const part = el.id
          ? '#' + el.id
          : getName(el) +
          (el.classList &&
            el.classList.value &&
            el.classList.value.trim() &&
            el.classList.value.trim().length
            ? '.' + el.classList.value.trim().replace(/\s+/g, '.')
            : '');
        if (sel.length + part.length > (100) - 1) return sel || part;
        sel = sel ? part + '>' + sel : part;
        if (el.id) break;
        node = el.parentNode;
      }
    } catch (err) {
      // Do nothing...
    }
    return sel;
  };

  const getNodesWithContentVisibility = (node) => {
    // Get the computed style
    let cs = window.getComputedStyle(node);
    let cv = cs['content-visibility'];

    // If we find content-visibility: auto, add it to the table
    if (cv && cv === 'auto') {
      ret.autoTable.push({ selector: getSelector(node), ContentVisibility: cs['content-visibility'] });
      ret.autoNodeArray.push(node);
    }

    // Recursively call this function for each child node
    for (let i = 0; i < node.children.length; i++) {
      getNodesWithContentVisibility(node.children[i]);
    }
  }

  // find all content-visibility: auto
  getNodesWithContentVisibility(document.body);

  // Display the results in the console
  if (ret.autoTable.length === 0) {
    console.log('%cNo content-visibility: auto found. Consider applying content-visibility: auto to offscreen content (the footer perhaps?)', 'color: orange; font-weight: bold;');
  } else {
    console.log('%cContent-visibility: auto selectors', 'color: green; font-weight: bold;');
    console.table(ret.autoTable);

    console.log('%cNodeList for you to inspect (harder to read but more info)', 'color: green; font-weight: bold;');
    console.log(ret.autoNodeArray);
  }
})()
