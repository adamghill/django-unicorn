import { contains } from "./utils.js";

/**
 * Encapsulate DOM element attribute for Unicorn-related information.
 */
export class Attribute {
  constructor(attribute) {
    this.attribute = attribute;
    this.name = this.attribute.name;
    this.value = this.attribute.value;
    this.isUnicorn = false;
    this.isModel = false;
    this.isPoll = false;
    this.isKey = false;
    this.isError = false;
    this.modifiers = {};
    this.eventType = null;

    this.init();
  }

  /**
   * Init the attribute.
   */
  init() {
    if (contains(this.name, "unicorn:") || contains(this.name, "uni:") || contains(this.name, "🦄:")) {
      this.isUnicorn = true;

      if (contains(this.name, "unicorn:model") || contains(this.name, "uni:model") || contains(this.name, "🦄:model")) {
        this.isModel = true;
      } else if (contains(this.name, "unicorn:poll") || contains(this.name, "uni:poll") || contains(this.name, "🦄:poll")) {
        this.isPoll = true;
      } else if (this.name === "unicorn:key" || this.name === "uni:key" || this.name === "🦄:key") {
        this.isKey = true;
      } else if (contains(this.name, "unicorn:error:") || contains(this.name, "uni:error:") || contains(this.name, "🦄:error:")) {
        this.isError = true;
      } else {
        const actionEventType = this.name.replace("unicorn:", "").replace("uni:", "").replace("🦄:", "");

        if (actionEventType !== "id" && actionEventType !== "name" && actionEventType !== "checksum") {
          this.eventType = actionEventType;
        }
      }

      let potentialModifiers = this.name;

      if (this.eventType) {
        potentialModifiers = this.eventType;
      }

      // Find modifiers and any potential arguments
      potentialModifiers.split(".").slice(1).forEach((modifier) => {
        const modifierArgs = modifier.split("-");
        this.modifiers[modifierArgs[0]] = modifierArgs.length > 1 ? modifierArgs[1] : true;

        // Remove any modifier from the event type
        if (this.eventType) {
          this.eventType = this.eventType.replace(`.${modifier}`, "");
        }
      });
    }
  }
}
