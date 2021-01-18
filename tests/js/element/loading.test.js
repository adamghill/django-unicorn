import test from "ava";
import { getElement } from "../utils.js";

test("loading class", (t) => {
  const html = "<div u:click='update()' u:loading.class='loading'></div>";
  const element = getElement(html);

  t.is(element.loading.classes.length, 1);
  t.is(element.loading.classes[0], "loading");
});

test("loading multiple classes", (t) => {
  const html =
    "<div u:click='update()' u:loading.class='loading another'></div>";
  const element = getElement(html);

  t.is(element.loading.classes.length, 2);
  t.is(element.loading.classes[0], "loading");
  t.is(element.loading.classes[1], "another");
});

test("loading remove class", (t) => {
  const html =
    "<div u:click='update()' u:loading.class.remove='unloading'></div>";
  const element = getElement(html);

  t.is(element.loading.removeClasses.length, 1);
  t.is(element.loading.removeClasses[0], "unloading");
});

test("loading multiple remove classes", (t) => {
  const html =
    "<div u:click='update()' u:loading.class.remove='unloading great'></div>";
  const element = getElement(html);

  t.is(element.loading.removeClasses.length, 2);
  t.is(element.loading.removeClasses[0], "unloading");
  t.is(element.loading.removeClasses[1], "great");
});

test("loading attr", (t) => {
  const html = "<div u:click='update()' u:loading.attr='disabled'></div>";
  const element = getElement(html);

  t.is(element.loading.attr, "disabled");
});
