# Cursor Rules

## 1. Design Systems vs Libraries: Bridging the Gap
- **Acknowledge Different Perspectives:**
  - Designers focus on consistency (tokens, spacing, typography, brand).
  - Developers focus on flexibility (props, reusability, configuration).
- **Bridge the Gap:**
  - When implementing or updating UI components, always consult both the design system and the component library documentation.
  - Ensure changes maintain both visual consistency and code flexibility.
  - Communicate with both designers and developers when introducing new patterns or components.
- **Decision-Making:**
  - Prioritize solutions that satisfy both consistency (design) and flexibility (development).
  - Avoid changes that benefit one perspective at the expense of the other.
- **Documentation:**
  - Document new components or patterns in both design and developer terms.
  - Reference the design system and component library in PRs and code comments when relevant.
- **Reference:**
  [Design Systems vs Libraries: Why Designers and Developers See Design Systems Differently](https://www.designsystemscollective.com/design-systems-vs-libraries-why-designers-and-developers-see-design-systems-differently-089e78800a1d)

---

## 2. Pydantic Models: Avoiding Circular References
- **No Direct Imports for Mutually-Referencing Schemas:**
  - If two Pydantic models reference each other, do **not** import one directly into the other. Use string-based forward references for type hints.
- **Always Use Forward References for Recursive Fields:**
  - For self-referencing or mutually-referencing fields, use a string type hint (e.g., `parent: 'Category'` or `members: List['User']`).
- **Call `.model_rebuild()` After All Models Are Defined:**
  - After defining all models (and after all imports), call `.model_rebuild()` on each model that uses forward references, ideally in your `schemas/__init__.py`.
- **Document Forward Reference Usage:**
  - Add a comment above any recursive or mutually-referencing field explaining the use of forward references and `.model_rebuild()`.
- **Test for RecursionError on Startup:**
  - If you encounter a `RecursionError` at import time, systematically comment out nested fields and reintroduce them with forward references and `.model_rebuild()`.

---

## 3. General Backend Rules
- **Environment Variables:**
  - Always check that required environment variables (like `DATABASE_URL`) are loaded before engine creation. Fail fast and clearly if missing.
- **No Mock Data in Dev/Prod:**
  - Only use mocking in tests, never in dev or prod environments.
- **Keep Files Manageable:**
  - Refactor files that exceed 200-300 lines.
- **Avoid Unnecessary Duplication:**
  - Reuse existing code and patterns; do not introduce new ones unless necessary.
- **Write Thorough Tests:**
  - All major functionality should have tests, especially after fixing bugs or refactoring.

---

These rules are intended to guide this project and others for maintainability, collaboration, and technical excellence. 