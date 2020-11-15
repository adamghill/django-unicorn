import test from "ava";
import { getElement } from "../utils.js";

test("loading class", (t) => {
  const html = "<div u:click='update()' u:loading.class='loading'></div>";
  const element = getElement(html);

  t.is(element.loading.class, "loading");
});

test("loading remove class", (t) => {
  const html = "<div u:click='update()' u:loading.class.remove='unloading'></div>";
  const element = getElement(html);

  t.is(element.loading.removeClass, "unloading");
});

test("loading attr", (t) => {
  const html = "<div u:click='update()' u:loading.attr='disabled'></div>";
  const element = getElement(html);

  t.is(element.loading.attr, "disabled");
});
