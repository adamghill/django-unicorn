export class AlpineMorpher {
  constructor(options) {
    this.options = options;
  }

  morph(dom, htmlElement) {
    // Note that we check if Alpine.morph is loaded not on instantiation, but on morph.
    // This is because at the time of instantiation, Alpine may not be loaded yet, as it's usually
    // loaded with <script defer>.
    this.ensureAlpineMorphInstalled();
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

  /**
   * Check if window has Alpine and Alpine Morph
   */
  ensureAlpineMorphInstalled() {
    if (!window.Alpine || !window.Alpine.morph) {
      throw Error(`
Alpine morpher requires Alpine to be loaded. Add Alpine and Alpine Morph to your page.
See https://www.django-unicorn.com/docs/custom-morphers/#alpine for more information.
`);
    }
  }

}
