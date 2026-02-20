module.exports = {
  root: true,
  parserOptions: {
    parser: "babel-eslint",
  },
  env: {
    browser: true,
  },
  extends: ["airbnb-base", "prettier"],
  rules: {
    "no-console": "warn",
    quotes: ["error", "double"],
    "max-len": ["error", { code: 140, ignoreStrings: true, ignoreUrls: true }],
    "import/no-unresolved": 0,
    "linebreak-style": 0,
    "comma-dangle": 0,
    "import/extensions": ["error", "always", { ignorePackages: true }],
    "import/prefer-default-export": 0,
    "no-unused-expressions": ["error", { allowTernary: true }],
    "no-underscore-dangle": 0,
    "no-param-reassign": 0,
    "object-curly-newline": ["error", { ObjectPattern: "never" }],
    "no-plusplus": ["error", { allowForLoopAfterthoughts: true }],
    "max-classes-per-file": 0,
  },
};
