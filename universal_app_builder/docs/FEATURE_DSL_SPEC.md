# Feature DSL Specification (Spec Stub)

**Status:** SPEC-STUB | **Implements:** No parser yet

## Goal
Provide a human-readable declarative format to describe app screens, components, navigation, and basic styling.

## Minimal Grammar (Phase 1 Target)
- Screens list
- Components: container, label, button, input
- Navigation: forward links by id
- Styling: palette names (semantic), spacing tokens

## Example (Conceptual)
```yaml
screens:
  - id: intro
    title: "Welcome"
    components:
      - type: label
        text: "Hello"
      - type: button
        text: "Continue"
        action: goto:account_setup
  - id: account_setup
    title: "Create Account"
    components:
      - type: input
        label: "Account Name"
```

## Validation Rules (Planned)
- Unique screen ids
- Referenced targets exist
- Component required fields present

## Deferred Features
- Data bindings
- Conditionals
- Advanced layout constraints

## Risks
Expanding grammar prematurely could create maintenance overhead.
