/**
 * This snippet will output all the elements that have a CSS transition on them.
 * 
 * To test for a transition, we check the computed style of the element and see if it has a transition property.
 * 
 * To test if the layout-shift is caused by a transition you could temporarily disable transitions by copying the CSS outputted in the console.
 * The use a RUM tool like Core/Dash (https://coredash.app) to see if the page layout shift is affected.
 */

(() => {
 
  let nodeTable = [];
  let nodeArray = [];

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

  const getNodesWithTransition = (node) => {

    // Get the computed style
    let cs = window.getComputedStyle(node);
    let tp = cs['transition-property'];

    // If there is a transition, add it to the table
    if (tp !== '' && tp !== 'none') {
      nodeTable.push({ selector: getSelector(node), transition: cs['transition'] });
      nodeArray.push(node);
    }

    // Recursively call this function for each child node
    for (let i = 0; i < node.children.length; i++) {
      getNodesWithTransition(node.children[i]);
    }
  }

  // Start the function
  getNodesWithTransition(document.body);

  // Display the results in the console
  console.log('%cReadable table of selectors and their transitions', 'color: red; font-weight: bold;');
  console.table(nodeTable);


  console.log('%cNodeList for you to inspect (harder to read but more info)', 'color: red; font-weight: bold;');

  console.log(nodeArray);


  //join all selectors by a comman
  let selectors = nodeTable.map((item) => item.selector).join(', ');

  console.log('%cSpecific CSS to disable all transitions on this page', 'color: red; font-weight: bold;');
  console.log(`<style>${selectors}:transition-property: none !important;</style>`);

  
  console.log('%cGlobal CSS to disable all transitions on this page (not suggested on production)', 'color: red; font-weight: bold;');
  console.log(`<style>*:transition-property: none !important;</style>`);

})()
