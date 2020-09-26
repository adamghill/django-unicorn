import { Attribute } from "./attribute.js";

/**
 * Encapsulate DOM element for Unicorn-related information.
 */
export class Element {
  constructor(el) {
    this.el = el;
    this.init();
  }

  /**
   * Init the element.
   */
  init() {
    this.id = this.el.id;
    this.isUnicorn = false;
    this.attributes = [];
    this.value = this.getValue();

    this.model = {};
    this.poll = {};
    this.actions = [];

    this.key = undefined;
    this.errors = [];

    if (!this.el.attributes) {
      return;
    }

    for (let i = 0; i < this.el.attributes.length; i++) {
      const attribute = new Attribute(this.el.attributes[i]);
      this.attributes.push(attribute);

      if (attribute.isUnicorn) {
        this.isUnicorn = true;
      }

      if (attribute.isModel) {
        this.model.name = attribute.value;
        this.model.eventType = attribute.modifiers.lazy ? "blur" : "input";
        this.model.isLazy = !!attribute.modifiers.lazy;
        this.model.isDefer = !!attribute.modifiers.defer;
        this.model.debounceTime = attribute.modifiers.debounce ? parseInt(attribute.modifiers.debounce, 10) || -1 : -1;
      } else if (attribute.isPoll) {
        this.poll.method = attribute.value ? attribute.value : "refresh";
        this.poll.timing = 2000;

        const pollArgs = attribute.name.split("-").slice(1);

        if (pollArgs.length > 0) {
          this.poll.timing = parseInt(pollArgs[0], 10) || 2000;
        }
      } else if (attribute.eventType) {
        const action = {};
        action.name = attribute.value;
        action.eventType = attribute.eventType;
        action.isPrevent = false;
        action.isStop = false;

        if (attribute.modifiers) {
          Object.keys(attribute.modifiers).forEach((modifier) => {
            if (modifier === "prevent") {
              action.isPrevent = true;
            } else if (modifier === "stop") {
              action.isStop = true;
            } else {
              // Assume the modifier is a keycode
              action.key = modifier;
            }
          });
        }

        this.actions.push(action);
      }

      if (attribute.isKey) {
        this.key = attribute.value;
      }

      if (attribute.isError) {
        const code = attribute.name.replace("unicorn:error:", "");
        this.errors.push({ code, message: attribute.value });
      }
    }
  }

  /**
   * Focuses the element.
   */
  focus() {
    this.el.focus();
  }

  /**
   * Gets the value from the element.
   */
  getValue() {
    let { value } = this.el;

    if (this.el.type) {
      if (this.el.type.toLowerCase() === "checkbox") {
        // Handle checkbox
        value = this.el.checked;
      } else if (this.el.type.toLowerCase() === "select-multiple") {
        // Handle multiple select options
        value = [];
        for (let i = 0; i < this.el.selectedOptions.length; i++) {
          value.push(this.el.selectedOptions[i].value);
        }
      }
    }

    return value;
  }

  /**
   * Sets the value of an element. Tries to deal with HTML weirdnesses.
   */
  setValue(val) {
    if (this.el.type.toLowerCase() === "radio") {
      // Handle radio buttons
      if (this.el.value === val) {
        this.el.checked = true;
      }
    } else if (this.el.type.toLowerCase() === "checkbox") {
      // Handle checkboxes
      this.el.checked = val;
    } else {
      this.el.value = val;
    }
  }

  /**
   * Add an error to the element.
   */
  addError(error) {
    this.errors.push(error);
    this.el.setAttribute(`unicorn:error:${error.code}`, error.message);
  }

  /**
   * Remove all errors from the element.
   */
  removeErrors() {
    this.errors.forEach((error) => {
      this.el.removeAttribute(`unicorn:error:${error.code}`);
    });

    this.errors = [];
  }
}
