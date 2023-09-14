export class AlpineMorpher {
  constructor(options) {
    // Check if window has Alpine and Alpine Morph
    if (!window.Alpine || !window.Alpine.morph) {
      throw Error(`
Alpine morpher requires Alpine to be loaded. Add Alpine and Alpine Morph to your page.
See https://www.django-unicorn.com/docs/custom-morphers/#alpine for more information.
`);
    }
    this.options = options;
  }

  morph(dom, htmlElement) {
    if (htmlElement) {
      return window.Alpine.morph(dom, htmlElement, this.getOptions());
    }
  }

  getOptions() {
    return {
      key(el) {
        if (el.attributes) {
          const key =
            el.getAttribute("unicorn:key") ||
            el.getAttribute("u:key") ||
            el.id;
          if (key) {
            return key;
          }
        }
        return el.id
      }
    }
  }
}
