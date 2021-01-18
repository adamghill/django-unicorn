import test from "ava";
import { getElement } from "../utils.js";

test("dirty class", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty' />";
  const element = getElement(html);

  t.is(element.dirty.classes.length, 1);
  t.is(element.dirty.classes[0], "dirty");
});

test("dirty multiple classes", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty another' />";
  const element = getElement(html);

  t.is(element.dirty.classes.length, 2);
  t.is(element.dirty.classes[0], "dirty");
  t.is(element.dirty.classes[1], "another");
});

test("dirty remove class", (t) => {
  const html = "<input u:model='name' u:dirty.class.remove='clean' />";
  const element = getElement(html);

  t.is(element.dirty.removeClasses.length, 1);
  t.is(element.dirty.removeClasses[0], "clean");
});

test("dirty multiple remove classes", (t) => {
  const html = "<input u:model='name' u:dirty.class.remove='clean great' />";
  const element = getElement(html);

  t.is(element.dirty.removeClasses.length, 2);
  t.is(element.dirty.removeClasses[0], "clean");
  t.is(element.dirty.removeClasses[1], "great");
});

test("dirty attr", (t) => {
  const html = "<input u:model='name' u:dirty.attr='disabled' />";
  const element = getElement(html);

  t.is(element.dirty.attr, "disabled");
});

test("dirty attr handleDirty", (t) => {
  const html = "<input u:model='name' u:dirty.attr='disabled' />";
  const element = getElement(html);

  t.is(element.el.getAttribute("disabled"), null);
  element.handleDirty();
  t.is(element.el.getAttribute("disabled"), "disabled");
});

test("dirty attr handleDirty revert", (t) => {
  const html =
    "<input u:model='name' u:dirty.attr='disabled' disabled='disabled' />";
  const element = getElement(html);

  t.is(element.el.getAttribute("disabled"), "disabled");
  element.handleDirty(true);
  t.is(element.el.getAttribute("disabled"), null);
});

test("dirty class handleDirty", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty' />";
  const element = getElement(html);

  t.is(element.el.classList.length, 0);
  element.handleDirty();
  t.is(element.el.classList.length, 1);
  t.is(element.el.classList[0], "dirty");
});

test("dirty multiple classes handleDirty", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty dirtier' />";
  const element = getElement(html);

  t.is(element.el.classList.length, 0);
  element.handleDirty();
  t.is(element.el.classList.length, 2);
  t.is(element.el.classList[0], "dirty");
  t.is(element.el.classList[1], "dirtier");
});

test("dirty class handleDirty revert", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty' class='dirty' />";
  const element = getElement(html);

  t.is(element.el.classList.length, 1);
  t.is(element.el.classList[0], "dirty");
  element.handleDirty(true);
  t.is(element.el.classList.length, 0);
});

test("dirty class handleDirty revert remove class attribute", (t) => {
  const html = "<input u:model='name' u:dirty.class='dirty' class='dirty' />";
  const element = getElement(html);

  t.is(element.el.getAttribute("class"), "dirty");
  element.handleDirty(true);
  t.is(element.el.getAttribute("class"), null);
});

test("dirty class.remove handleDirty", (t) => {
  const html =
    "<input u:model='name' u:dirty.class.remove='clean' class='clean' />";
  const element = getElement(html);

  t.is(element.el.classList.length, 1);
  t.is(element.el.classList[0], "clean");
  element.handleDirty();
  t.is(element.el.classList.length, 0);
});

test("dirty class.remove handleDirty revert", (t) => {
  const html = "<input u:model='name' u:dirty.class.remove='clean' class='' />";
  const element = getElement(html);

  t.is(element.el.classList.length, 0);
  element.handleDirty(true);
  t.is(element.el.classList.length, 1);
  t.is(element.el.classList[0], "clean");
});
