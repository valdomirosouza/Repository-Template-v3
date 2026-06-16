// Ambient declarations for CSS side-effect imports.
// TypeScript 6.0 enforces TS2882 (no type declaration for side-effect imports of
// non-code modules), which breaks `import "./globals.css"`. Next.js handles CSS at
// build time; these declarations satisfy the type checker without affecting runtime.
declare module "*.css";
declare module "*.scss";
