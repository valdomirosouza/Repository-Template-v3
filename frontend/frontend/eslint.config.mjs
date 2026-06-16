// ESLint flat config (ESLint 10 / Next.js 16).
// Next 16 removed `next lint` and the legacy `.eslintrc` workflow; eslint-config-next@16
// ships native flat-config arrays at ./core-web-vitals and ./typescript.
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = [
  // A config object with only `ignores` sets global ignores (replaces the old
  // `ignorePatterns` from .eslintrc.json — the generated OpenAPI client is not linted).
  { ignores: ["src/lib/api/**", ".next/**", "out/**", "node_modules/**", "coverage/**"] },
  ...nextCoreWebVitals,
  ...nextTypescript,
];

export default eslintConfig;
