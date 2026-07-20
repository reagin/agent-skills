---
name: frontend-file-structure
description: Use for React TypeScript file-structure work involving ownership or folders for new or moved files, multi-file components with narrow public entries, page and route separation, mirrored tests, path naming, import aliases, or directory-tree review. Trigger only when placement is unresolved or structure must change. Do not use for UI, logic, performance, security, upgrades, or debugging, or for code and tests whose path and structure are already established.
---

# Frontend File Structure

Organize React TypeScript code by technical responsibility while keeping closely related implementation details together. Apply these rules when proposing a structure, creating files, extending an existing project, or reviewing placement and naming.

## Inspect Before Creating Files

Inspect the current project before choosing a path:

1. Locate the source root, usually `src/`.
2. Identify the framework, router, state library, test runner, styling system, and configured path aliases. Read the effective `tsconfig` chain, including referenced or extended application configs, before choosing import paths.
3. Inspect nearby files and existing public entries.
4. Preserve framework-required files and established tool conventions.
5. Apply this skill strictly to new files and the files directly touched by the task.

Do not reorganize unrelated code merely to make the whole repository conform. If ownership remains materially ambiguous after inspection, ask which module should own the file before creating it.

## Use Responsibility Directories

Prefer this source layout when the corresponding responsibilities exist:

```text
src/
├── components/
├── hooks/
├── utils/
├── stores/
├── constants/
├── pages/
├── routes/
├── styles/
├── tests/
└── types/       # only when global or truly cross-domain types are needed
```

Do not create empty directories. Add a directory only when the task introduces that responsibility.

| Directory | Owns |
| --- | --- |
| `components/` | Reusable UI and component-owned implementation details |
| `hooks/` | Shared React hooks used outside one component module |
| `utils/` | Shared pure helpers with no UI ownership |
| `stores/` | Shared client state stores and store-specific types/selectors |
| `constants/` | Shared stable values, keys, enums, and configuration constants |
| `pages/` | Route-level screens and page composition |
| `routes/` | Route objects, route trees, guards, loaders, and router assembly |
| `styles/` | Global styles, themes, tokens, resets, and shared style foundations |
| `tests/` | Tests mirroring the source tree |
| `types/` | Global declarations, environment types, or truly cross-domain contracts |

Responsibility directories may contain matching domain subdirectories when a domain has several related files, for example `components/subscription/`, `hooks/subscription/`, and `utils/subscription/`. Keep each file in its responsibility directory; do not introduce a parallel `features/` hierarchy.

## Name Authored Files and Directories in Kebab-Case

Use lowercase kebab-case for authored file and directory names:

```text
profile-badge.tsx
use-current-profile.ts
format-profile-name.ts
audit-filter.store.ts
auth.routes.tsx
file-viewer.module.css
```

Keep conventional names such as `index.ts`, framework-mandated names, generated files, and tool configuration names unchanged. Use PascalCase for React component symbols and camelCase for functions or variables inside the files.

Avoid authored PascalCase or camelCase paths such as `ProfileBadge.tsx`, `useCurrentProfile.ts`, or `auditFilterStore.ts`.

## Prefer Named Exports

Use named exports for components, hooks, utilities, stores, route definitions, constants, and types:

```ts
export function FileViewer(props: FileViewerProps) {
  // ...
}
```

Use a default export only when a framework API, lazy-loading boundary, or established local convention requires one. Do not add both named and default exports for convenience.

## Keep Simple Components as Single Files

Keep a component directly under `components/` while it has no companion source file:

```text
src/components/profile-badge.tsx
src/tests/components/profile-badge.test.tsx
```

Do not create one-file component directories preemptively.

## Promote Complex Components to Same-Name Directories

As soon as a component needs any companion implementation file, move it into a same-name directory and add a narrow `index.ts` public entry:

```text
src/components/file-viewer/
├── file-viewer.tsx
├── file-viewer-toolbar.tsx
├── file-viewer.types.ts
├── file-viewer.utils.ts
├── file-viewer.constants.ts
├── use-file-viewer.ts
├── file-viewer.module.css
└── index.ts

src/tests/components/file-viewer/
├── file-viewer.test.tsx
└── file-viewer.utils.test.ts
```

Companion files include private subcomponents, component-specific hooks, types, constants, utilities, styles, or other implementation modules. Complexity is based on ownership, not line count.

Export only the supported public API from `index.ts`:

```ts
export { FileViewer } from './file-viewer';
export type { FileViewerProps } from './file-viewer.types';
```

Do not export private toolbars, internal hooks, implementation helpers, constants, or styles. Consumers outside the directory import from the directory public entry. Files inside the directory may use relative imports.

## Colocate First, Promote When Shared

Place code with its narrowest clear owner:

- Keep a hook used only by one complex component inside that component directory.
- Keep component-specific types, constants, utilities, and CSS Modules beside the component.
- Keep page-specific styles beside the page when the project already follows colocated page styles; otherwise place them under a clearly named path in `styles/`.
- Move a hook to `hooks/`, a helper to `utils/`, or a constant to `constants/` only when it is reused across owners or has an independent application responsibility.
- Move types to `types/` only when they are global, environment-level, or truly cross-domain. Otherwise keep them with the component, hook, store, route, API module, or domain that owns them.

Do not make `types/`, `utils/`, or `constants/` a dumping ground. When moving shared code, move its tests to the matching mirrored test path.

## Separate Pages from Routes

Pages render route-level UI. Routes own navigation configuration.

```text
src/pages/audit-log-page.tsx
src/routes/audit.routes.tsx
src/routes/index.ts
src/tests/pages/audit-log-page.test.tsx
src/tests/routes/audit.routes.test.tsx
```

Split route configuration by coherent area, such as `auth.routes.tsx` and `chat.routes.tsx`, then assemble or expose it through `routes/index.ts`. Route modules may import pages; pages must not own route objects or import route internals merely to render UI.

When the effective `tsconfig` defines `@/*` for `src/*`, cross-directory imports use that alias:

```ts
import { AuditLogPage } from '@/pages/audit-log-page';
import { useAuditFilterStore } from '@/stores/audit-filter.store';
```

## Mirror Tests Under `src/tests`

Place unit, component, hook, store, utility, page, and route tests under `src/tests/`, mirroring the source path after `src/`:

```text
src/components/profile-badge.tsx
src/tests/components/profile-badge.test.tsx

src/hooks/use-current-profile.ts
src/tests/hooks/use-current-profile.test.ts

src/stores/audit-filter.store.ts
src/tests/stores/audit-filter.store.test.ts
```

Do not colocate these tests beside source files and do not flatten unrelated test responsibilities into `src/tests/`. Follow an E2E framework's required root convention, such as `e2e/`, for end-to-end suites when applicable.

Tests for a complex component should consume its public directory entry. Test private helpers separately only when their behavior warrants a dedicated contract; do not broaden `index.ts` merely to make private code importable.

## Preserve Dependency Direction

Keep dependencies flowing toward lower-level responsibilities:

- Routes may import pages.
- Pages may compose components, hooks, and stores.
- Components may use shared hooks, utilities, constants, and types.
- Hooks and stores may use utilities, constants, and shared contracts.
- Shared utilities must not depend on pages or components.

If a shared module needs a type currently owned by a component implementation, relocate the stable contract to the narrowest neutral owner instead of importing upward from the component.

Treat a store as a store even when its library exposes a hook-shaped API such as `useAuditFilterStore`; place it in `stores/`, not `hooks/`.

## Respect Existing Tooling

Derive the import strategy from the project's effective TypeScript configuration before generating imports. Apply these rules in order:

1. If `compilerOptions.paths` defines `@` or `@/*` for the source root, use `@/` for imports that cross responsibility or ownership directories. This includes routes importing pages, pages importing components or stores, and tests under `src/tests/` importing source modules.
2. Keep short relative imports inside the same owning directory or complex component module. These imports make the local cohesion visible and do not need the alias.
3. If the effective `tsconfig` defines no applicable alias, fall back to valid relative imports. Do not invent `@`, edit configuration, or assume that Vite defaults provide it.

```ts
// @/* -> src/* exists: cross-directory imports use the alias.
import { AuditLogPage } from '@/pages/audit-log-page';
import { formatAuditDate } from '@/utils/format-audit-date';

// Same directory: keep the relationship local.
export { auditRoutes } from './audit.routes';

// No alias exists: fall back to a relative path.
import { AuditLogPage } from '../pages/audit-log-page';
```

An `@` mapping in `tsconfig` is the deciding signal even when nearby files mix alias and relative styles. Verify that the bundler, test runner, linter, and framework resolver support the same mapping. If those resolvers disagree with `tsconfig`, report the configuration mismatch and update them only when configuration changes are within the task scope.

Framework and tooling contracts override generic layout preferences. Examples include generated route trees, Next.js route files, Remix route conventions, and test-runner setup files. Keep such files where the framework expects them while applying naming and ownership rules to ordinary authored modules.

## File-Creation Checklist

Before finishing a change, verify:

1. Every new file has one clear owner and responsibility.
2. Authored paths use kebab-case unless a framework or tool requires another name.
3. A component directory exists only because the component has companion files.
4. Each complex component has a narrow `index.ts` and private files remain private.
5. Tests live under mirrored `src/tests/` paths, except tool-mandated E2E layouts.
6. Pages render UI while routes own route construction.
7. Named exports are used unless a documented constraint requires a default export.
8. No `features/` directory, empty scaffolding, broad barrel, or unrelated migration was introduced.
9. Cross-directory imports use the configured `@/` alias; if no alias exists, they use valid relative paths. Same-directory imports remain relative.
10. Existing validation, type-checking, and relevant tests pass when the project provides them.

When reporting the result, list created or moved files and briefly explain any intentional exception to these rules.
