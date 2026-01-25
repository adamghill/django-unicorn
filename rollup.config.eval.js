import filesize from "rollup-plugin-filesize";
import terser from "@rollup/plugin-terser";
import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import babel from "@rollup/plugin-babel";
import versionInjector from "rollup-plugin-version-injector";
import alias from "@rollup/plugin-alias";
import path from "path";

import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRootDir = __dirname;

const commonPlugins = [
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
];

export default [
    // Nanomorph Build
    {
        input: "src/django_unicorn/static/unicorn/js/unicorn.js",
        output: {
            file: "src/django_unicorn/static/unicorn/js/unicorn.nanomorph.min.js",
            format: "iife",
            name: "Unicorn",
        },
        plugins: [
            alias({
                entries: [
                    { find: './morpher.js', replacement: path.resolve(projectRootDir, 'src/django_unicorn/static/unicorn/js/morpher-nanomorph.js') }
                ]
            }),
            ...commonPlugins
        ],
    },
    // Idiomorph Build
    {
        input: "src/django_unicorn/static/unicorn/js/unicorn.js",
        output: {
            file: "src/django_unicorn/static/unicorn/js/unicorn.idiomorph.min.js",
            format: "iife",
            name: "Unicorn",
        },
        plugins: [
            alias({
                entries: [
                    { find: './morpher.js', replacement: path.resolve(projectRootDir, 'src/django_unicorn/static/unicorn/js/morpher-idiomorph.js') }
                ]
            }),
            ...commonPlugins
        ],
    }
];
