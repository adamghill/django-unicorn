export class AlpineMorpher {
  constructor(options) {
    this.options = options;
  }

  morph(dom, htmlElement) {
    if (htmlElement) {
      // Check if window has Alpine and Alpine Morph
      if (!window.Alpine || !window.Alpine.morph) {
        throw Error(`
  Alpine.js and the Alpine morph plugin can not be found.
  See https://www.django-unicorn.com/docs/custom-morphers/#alpine for more information.
  `);
      }

      return window.Alpine.morph(dom, htmlElement, this.getOptions());
    }
  }

  getOptions() {
    return {
      key(el) {
        if (el.attributes) {
          const key =
            el.getAttribute("unicorn:key") || el.getAttribute("u:key") || el.id;

          if (key) {
            return key;
          }
        }

        return el.id;
      },
    };
  }
}
