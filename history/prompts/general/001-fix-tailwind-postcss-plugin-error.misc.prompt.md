---
id: "001"
title: "Fix Tailwind PostCSS Plugin Error"
stage: "misc"
date_iso: "2025-12-21"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "003-rag-chatbot"
user: "i7 4th"
command: "/sp.phr"
labels: ["tailwind-css", "postcss", "docusaurus", "build-error", "dependency"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "postcss.config.js"
  - "package.json"
tests: []
---

# Fix Tailwind PostCSS Plugin Error

## Prompt Text
```
fix and solve this error
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin. The PostCSS plugin has moved to a separate package, so to continue using Tailwind CSS with PostCSS you'll need to install `@tailwindcss/postcss` and update your PostCSS configuration.
-- inner error --
Error: It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin. The PostCSS plugin has moved to a separate package, so to continue using Tailwind CSS with PostCSS you'll need to install `@tailwindcss/postcss` and update your PostCSS configuration.
Generated code for G:\hacka\physical-ai-textbook-final\node_modules\css-loader\dist\cjs.js??ruleSet[1].rules[7].use[1]!G:\hacka\physical-ai-textbook-final\node_modules\postcss-loader\dist\cjs.js??ruleSet[1].rules[7].use[2]!G:\hacka\physical-ai-textbook-final\node_modules\@docusaurus\theme-classic\lib\theme\DocItem\Layout\styles.module.css
```

## Response Text
Successfully fixed the Tailwind CSS PostCSS plugin error by installing the @tailwindcss/postcss package and updating postcss.config.js to use the correct plugin name.

## Outcome Impact
Resolved the build error that occurred when using Tailwind CSS v4+ with PostCSS. The error was caused by using the direct tailwindcss plugin instead of the new separate @tailwindcss/postcss package required for Tailwind v4+.

## Tests Summary
None - configuration fix

## Files Summary
- postcss.config.js: Updated from 'tailwindcss: {}' to '@tailwindcss/postcss: {}'
- package.json: Added @tailwindcss/postcss as dev dependency

## Next Prompts
None

## Reflection Note
Tailwind CSS v4+ requires a separate PostCSS plugin package, which is a breaking change from earlier versions.

## Evaluation Notes
**Failure modes observed:** None - the fix was straightforward and successful.

**Next experiment to improve prompt quality:** None needed - the solution was clear and effective.
