import { Attribute } from "./attribute.js";
import { isEmpty, generateDbKey, hasValue } from "./utils.js";

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
    this.parent = null;

    if (this.el.parentElement) {
      this.parent = new Element(this.el.parentElement);
    }

    this.model = {};
    this.poll = {};
    this.loading = {};
    this.actions = [];
    this.db = {};
    this.field = {};
    this.target = null;
    this.key = null;
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
        this.model.debounceTime = attribute.modifiers.debounce
          ? parseInt(attribute.modifiers.debounce, 10) || -1
          : -1;
      } else if (attribute.isField) {
        this.field.name = attribute.value;
        this.field.eventType = attribute.modifiers.lazy ? "blur" : "input";
        this.field.isLazy = !!attribute.modifiers.lazy;
        this.field.isDefer = !!attribute.modifiers.defer;
        this.field.debounceTime = attribute.modifiers.debounce
          ? parseInt(attribute.modifiers.debounce, 10) || -1
          : -1;
      } else if (attribute.isDb) {
        this.db.name = attribute.value;
      } else if (attribute.isPK) {
        this.db.pk = attribute.value;
      } else if (attribute.isPoll) {
        this.poll.method = attribute.value ? attribute.value : "refresh";
        this.poll.timing = 2000;

        const pollArgs = attribute.name.split("-").slice(1);

        if (pollArgs.length > 0) {
          this.poll.timing = parseInt(pollArgs[0], 10) || 2000;
        }
      } else if (attribute.isLoading) {
        if (attribute.modifiers.attr) {
          this.loading.attr = attribute.value;
        } else if (attribute.modifiers.class && attribute.modifiers.remove) {
          this.loading.removeClass = attribute.value;
        } else if (attribute.modifiers.class) {
          this.loading.class = attribute.value;
        } else if (attribute.modifiers.remove) {
          this.loading.hide = true;
        } else {
          this.loading.show = true;
        }
      } else if (attribute.isTarget) {
        this.target = attribute.value;
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

    // Look in parent elements if the db.pk or db.name is missing
    if (this.isUnicorn && hasValue(this.field)) {
      const dbAttrs = ["pk", "name"];
      let elToCheck = this;

      // Look for `db.pk` and `db.name`
      dbAttrs.forEach((attr) => {
        elToCheck = this;

        while (isEmpty(this.db[attr])) {
          if (elToCheck.el.getAttribute("unicorn:checksum")) {
            // A litte hacky, but stop looking after you hit the beginning of the component
            break;
          }

          if (elToCheck.isUnicorn && hasValue(elToCheck.db[attr])) {
            this.db[attr] = elToCheck.db[attr];
          }

          elToCheck = elToCheck.parent;
        }
      });

      // Look for model.name
      elToCheck = this;

      while (isEmpty(this.model.name)) {
        if (elToCheck.el.getAttribute("unicorn:checksum")) {
          // A litte hacky, but stop looking after you hit the beginning of the component
          break;
        }

        if (elToCheck.isUnicorn && hasValue(elToCheck.model.name)) {
          if (hasValue(this.field) && isEmpty(this.db)) {
            // Handle a model + field that is not a db
            this.model = this.field; // Make sure to keep all modifiers from the field for the model
            this.model.name = `${elToCheck.model.name}.${this.field.name}`;
            this.field = {};
          } else {
            this.model.name = elToCheck.model.name;
          }
        }

        elToCheck = elToCheck.parent;
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
   * Hide the element.
   */
  hide() {
    this.el.hidden = "hidden";
  }

  /**
   * Show the element.
   */
  show() {
    this.el.hidden = null;
  }

  /**
   * A key that takes into consideration the db name and pk.
   */
  dbKey() {
    return generateDbKey(this);
  }

  /**
   * Get the element's next parent that is a unicorn element.
   *
   * Returns `null` if no unicorn element can be found before the root.
   */
  getUnicornParent() {
    let parentElement = this.parent;

    while (parentElement && !parentElement.isUnicorn) {
      if (parentElement.el.getAttribute("unicorn:checksum")) {
        return null;
      }

      parentElement = parentElement.parent;
    }

    return parentElement;
  }

  /**
   * Check if another `Element` is the same as this `Element`.
   * @param {Element} other
   */
  isSame(other) {
    // Use isSameNode (not isEqualNode) because we want to check the nodes reference the same object
    return this.el.isSameNode(other.el);
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
    if (isEmpty(this.el.type)) {
      return;
    }

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
