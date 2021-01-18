export const MORPHDOM_OPTIONS = {
  childrenOnly: false,
  // eslint-disable-next-line consistent-return
  getNodeKey(node) {
    // A node's unique identifier. Used to rearrange elements rather than
    // creating and destroying an element that already exists.
    if (node.attributes) {
      const key =
        node.getAttribute("unicorn:key") ||
        node.getAttribute("u:key") ||
        node.id;

      if (key) {
        return key;
      }
    }
  },
  // eslint-disable-next-line consistent-return
  onBeforeElUpdated(fromEl, toEl) {
    // Because morphdom also supports vDom nodes, it uses isSameNode to detect
    // sameness. When dealing with DOM nodes, we want isEqualNode, otherwise
    // isSameNode will ALWAYS return false.
    if (fromEl.isEqualNode(toEl)) {
      return false;
    }
  },
};
