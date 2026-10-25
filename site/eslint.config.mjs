// ESLint 配置：抓「几乎肯定是 bug」的问题，不追求风格统一。
//
// 关键点：本项目有两类 JS，语法模式不同，必须分开配置：
//   .mjs        → ES module（测试脚本用 import）
//   .cjs / .js  → CommonJS（浏览器内联脚本风格）
// 另外必须忽略构建产物（神智核*.html），否则会把几 MB 的内联脚本
// 当成一个文件来扫，行号全变成 1:xxxxx，毫无意义。
import globals from "globals";

const SHARED = {
  "no-undef": "error",
  "no-unused-vars": ["warn", { args: "none", varsIgnorePattern: "^_|^e$|^err$" }],
  "no-dupe-keys": "error",
  "no-dupe-args": "error",
  "no-unreachable": "error",
  "no-cond-assign": "error",
  "no-constant-condition": ["error", { checkLoops: false }],
  "no-func-assign": "error",
  "no-obj-calls": "error",
  "no-sparse-arrays": "error",
  "no-unsafe-negation": "error",
  "use-isnan": "error",
  "valid-typeof": "error",
  "no-self-assign": "error",
  "no-self-compare": "error",
};

export default [
  {
    // 忽略：依赖、构建产物、测试用单档 HTML、由 build 注入的片段，
    // 以及 headless Chrome 的临时 profile（内含浏览器扩展的 JS，不属本项目）
    ignores: [
      "node_modules/**",
      "_t_profile*/**",
      "神智核*.html",
      "_t_*.html",
      "_appcheck.js",
      "_check_main.js",
      "extras.js",
      "template.html",
    ],
  },
  // ---- ES module 脚本（.mjs）----
  {
    files: ["**/*.mjs"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.node, ...globals.browser },
    },
    rules: SHARED,
  },
  // ---- CommonJS（.cjs，以及站点内联脚本风格的 .js）----
  {
    files: ["**/*.cjs", "**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "commonjs",
      globals: {
        ...globals.node, ...globals.browser,
        // Playwright 的 page.evaluate 回调在浏览器上下文执行，
        // 里面会引用页面内的全局变量（如 SUB），这是正常的，不算未定义。
        SUB: "readonly", TOPICS: "readonly", UNITS: "readonly",
        SUBJECTS: "readonly", mdLite: "readonly",
      },
    },
    rules: SHARED,
  },
];
