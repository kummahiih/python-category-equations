# Lean encodings for a Set-reading identity

**Caveat (read first):** This directory formalizes a **Set + products** reading of the identity
`f1 ▷ (f2, I) ▷ f3`. It is **not** a formalization of the repository’s Python `*` algebra.

- In Python, `C(a,b)` is the union of generators; the closest cousin in the root README is
  `C(1)*(C(2)+I)*C(3)`, which is about connecting sources to sinks, **not** function fan-out.
- The `I` appearing here is the ordinary identity function `id`, **not** the singleton identity
  term `I` of the Python algebra.

Pinned to Lean `v4.34.0`. No Mathlib. Build from the **repository root**:

```bash
lake build
```

The Lean file defines safe combinators (`I`, `pipe`/`⊳`, `branch`, `mapPair`) that avoid
clashing with Lean’s built-in pipe and product notations, and proves the corresponding
equality of functions `A → C × C`.

See `CategoryEquations.lean` for the definitions and the lemma `pipe_branch_mapPair`.
