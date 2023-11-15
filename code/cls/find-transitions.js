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
  console.log('%cNodes that have a transition', 'color: red; font-weight: bold;');
  console.table(nodeTable);
  console.log(nodeArray);

})()
