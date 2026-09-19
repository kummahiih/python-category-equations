/--
Safe encodings for the Set-reading of the f1 ▷ (f2, I) ▷ f3 identity.
No infixl |>, no pair macros: those clash with Lean pipe and products.
Both sides of the intended lemma are A → C × C.
`Type*` is Mathlib notation; this package has no Mathlib, so binders use `Type _`.
-/

def I {α : Type _} : α → α := id

def pipe {α β γ : Type _} (f : α → β) (g : β → γ) : α → γ := g ∘ f

infix:50 " ⊳ " => pipe

def branch {α β γ : Type _} (f : α → β) (g : α → γ) : α → β × γ :=
  fun a => (f a, g a)

def mapPair {α β : Type _} (f : α → β) : α × α → β × β :=
  fun p => (f p.1, f p.2)

/-- The Set-reading identity: f1 ⊳ (f2, I) ⊳ f3 = (f1 ⊳ f2 ⊳ f3, f1 ⊳ f3). -/
theorem pipe_branch_mapPair
    {A B C : Type _} (f1 : A → B) (f2 : B → B) (f3 : B → C) :
    pipe (pipe f1 (branch f2 I)) (mapPair f3) =
      branch (pipe (pipe f1 f2) f3) (pipe f1 f3) := by
  funext a
  rfl
