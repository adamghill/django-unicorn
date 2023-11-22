import filesize from "rollup-plugin-filesize";
import { terser } from "rollup-plugin-terser";
import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import babel from "@rollup/plugin-babel";
import versionInjector from "rollup-plugin-version-injector";

export default {
  input: "django_unicorn/static/unicorn/js/unicorn.js",
  output: {
    file: "django_unicorn/static/unicorn/js/unicorn.min.js",
    format: "iife",
    name: "Unicorn",
  },
  plugins: [
    resolve(),
    terser({
      mangle: true,
    }),
    versionInjector({
      injectInComments: {
        fileRegexp: /\.js$/,
        tag: "Version: {version}",
        dateFormat: "mmmm d, yyyy HH:MM:ss",
      }
    }),
    commonjs({}),
    babel({ babelHelpers: "bundled" }),
    filesize(),
  ],
};
