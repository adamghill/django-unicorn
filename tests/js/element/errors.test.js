import test from "ava";
import { getElement } from "../utils.js";

test("unicorn:error:required", (t) => {
  const html = "<input unicorn:model='name' unicorn:error:required='This field is required.'></input>";
  const element = getElement(html);

  t.is(element.errors.length, 1);
  const error = element.errors[0];
  t.is(error.code, "required");
  t.is(error.message, "This field is required.");
});

test("unicorn:error:invalid", (t) => {
  const html = "<input unicorn:model='name' unicorn:error:invalid='Enter a whole number.'></input>";
  const element = getElement(html);

  t.is(element.errors.length, 1);
  const error = element.errors[0];
  t.is(error.code, "invalid");
  t.is(error.message, "Enter a whole number.");
});

test("addError()", (t) => {
  const html = "<input unicorn:model='name'></input>";
  const element = getElement(html);

  t.is(element.errors.length, 0);
  element.addError({ code: "invalid", message: "Enter a whole number." });
  t.is(element.errors.length, 1);
  t.is(element.el.getAttribute("unicorn:error:invalid"), "Enter a whole number.");
});

test("removeErrors()", (t) => {
  const html = "<input unicorn:model='name' unicorn:error:invalid='Enter a whole number.'></input>";
  const element = getElement(html);

  t.is(element.errors.length, 1);
  element.removeErrors();
  t.is(element.errors.length, 0);
});
