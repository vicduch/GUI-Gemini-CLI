# Framework de Développement Logiciel, Ressources et Matrice de Compétences

Contexte: projet Python 3.12+, GTK4/Libadwaita, VTE, GLib, IPC Unix sockets, tests headless.

## 1) Le framework de travail que j’utilise

Je fonctionne avec une méthode **Architecture-first + TDD + Risk-driven delivery**.

### 1.1 Architecture-first
- Définir les frontières de responsabilité avant de coder.
- Exemple ici:
  - `core/`: process management, IPC, état, orchestration.
  - `ui/`: widgets, vues, interactions utilisateur.
- Objectif: éviter les couplages cachés qui explosent en maintenance.

### 1.2 TDD pragmatique
- Boucle courte: **test rouge -> implémentation minimale -> refactor**.
- Les tests couvrent d’abord les scénarios critiques: erreurs, timeouts, race conditions, nettoyage de ressources.

### 1.3 Delivery orientée risques
- Prioriser ce qui casse la prod en premier:
  1. blocage loop GTK
  2. fuite de file descriptors/watchers
  3. corruption état process/session
  4. UX incohérente lors transitions focus/grid
- Traiter les points à plus fort impact avant les optimisations esthétiques.

### 1.4 Boucle qualité continue
- Gates minimaux:
  - `ruff check .`
  - `mypy core`
  - `xvfb-run -a pytest -q`
- Chaque PR doit être testable/reviewable de manière déterministe.

## 2) Méthode concrète de développement (pas à pas)

1. **Cadrage**
- Écrire le besoin en comportements observables (pas en implémentation).
- Définir critères d’acceptation (success/failure).

2. **Design technique léger**
- Diagramme simple des flux (UI -> core -> process -> IPC -> UI).
- Identifier invariants (ex: un process par session active).

3. **Plan de travail découpé**
- Work packages petits (1 responsabilité par lot).
- Un commit logique par lot.

4. **Implémentation TDD**
- Commencer par tests unitaires.
- Ajouter tests intégration pour GLib/IPC/GTK.

5. **Durcissement**
- Cas limites: callbacks fautifs, IO_HUP/ERR, kill timeout, réentrance UI.

6. **Validation & documentation**
- Lancer les gates.
- Mettre à jour docs opérationnelles (`GEMINI.md`, plans, notes API).

## 3) Ressources pour apprendre sérieusement

## 3.1 Fondations software engineering
- *Clean Architecture* — Robert C. Martin
- *Designing Data-Intensive Applications* — Martin Kleppmann
- *The Pragmatic Programmer* — Hunt & Thomas
- *Refactoring* — Martin Fowler

## 3.2 Python avancé
- Python docs (typing, asyncio, dataclasses): https://docs.python.org/3/
- PEP 484 (typing), PEP 544 (Protocols), PEP 695 (type params)
- `mypy` docs: https://mypy.readthedocs.io/
- `ruff` docs: https://docs.astral.sh/ruff/

## 3.3 GTK4 / Libadwaita / PyGObject
- PyGObject guide: https://pygobject.gnome.org/
- GTK4 reference: https://docs.gtk.org/gtk4/
- Libadwaita reference: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/
- VTE docs: https://gnome.pages.gitlab.gnome.org/vte/

## 3.4 Testing
- pytest: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Martin Fowler - Test Pyramid: https://martinfowler.com/articles/practical-test-pyramid.html

## 3.5 Concurrence, fiabilité, ops
- *Release It!* — Michael Nygard
- *Site Reliability Engineering* (Google): https://sre.google/books/

## 4) Parcours d’apprentissage recommandé (12 semaines)

### Semaines 1-2: Base solide
- Python typing strict, exceptions, dataclasses, logs structurés.
- Exercice: mini service IPC newline JSON avec tests fragmentation UTF-8.

### Semaines 3-4: Asynchrone et événements
- Event loops, IO non bloquant, timeouts, cancellation.
- Exercice: process manager mock (spawn/stop/hot-reload) + tests race.

### Semaines 5-6: UI GTK4
- Widgets, layout, signaux, lifecycle.
- Exercice: stack grid/focus avec transitions idempotentes.

### Semaines 7-8: Architecture
- Dépendances unidirectionnelles core/ui.
- Exercice: refactor d’un module couplé en ports/adapters simples.

### Semaines 9-10: Qualité et CI
- Ruff/mypy/pytest en pipeline.
- Exercice: pipeline headless Xvfb, tests stables 3 runs consécutifs.

### Semaines 11-12: Projet intégrateur
- Build d’un mini orchestrateur terminal multi-session.
- Livraison: docs + tests + revue architecture + plan hardening.

## 5) Matrice de compétences (complète) pour un projet comme celui-ci

Légende des niveaux:
- **N0**: notions
- **N1**: junior autonome sur tâches simples
- **N2**: intermédiaire fiable en prod
- **N3**: senior capable de design/mentorat
- **N4**: expert/pilier technique

| Domaine | Compétence | N0 | N1 | N2 | N3 | N4 |
|---|---|---:|---:|---:|---:|---:|
| Python | Syntaxe, stdlib, packaging | x | x | x | x | x |
| Python | Typage strict (`mypy`) |  | x | x | x | x |
| Python | API design robuste |  |  | x | x | x |
| Asynchrone | I/O non bloquant |  | x | x | x | x |
| Asynchrone | Gestion timeouts/cancel/retry |  |  | x | x | x |
| Asynchrone | Analyse race conditions |  |  |  | x | x |
| Process | spawn/stop/reload fiable |  | x | x | x | x |
| Process | Gestion signaux Unix |  | x | x | x | x |
| IPC | Unix sockets + framing newline JSON |  | x | x | x | x |
| IPC | Fragmentation UTF-8 / robustesse decode |  |  | x | x | x |
| GTK4 | Layout, widgets, signaux |  | x | x | x | x |
| GTK4 | Lifecycle et non-blocage main loop |  |  | x | x | x |
| UI/UX | États UI cohérents (focus/grid) |  | x | x | x | x |
| Architecture | Séparation core/ui stricte |  | x | x | x | x |
| Architecture | Contrats d’interface stables |  |  | x | x | x |
| Tests | Unit tests TDD |  | x | x | x | x |
| Tests | Integration tests GLib/GTK headless |  |  | x | x | x |
| Tests | Tests de non-régression asynchrone |  |  | x | x | x |
| Qualité | Lint + format + conventions |  | x | x | x | x |
| Qualité | Type-check gating CI |  |  | x | x | x |
| CI/CD | Pipelines fiables Linux headless |  | x | x | x | x |
| Observabilité | Logs structurés corrélables |  |  | x | x | x |
| Observabilité | Debug prod multi-processus |  |  |  | x | x |
| Sécurité | Gestion secrets/tokens |  | x | x | x | x |
| Collaboration | PRs claires, revue orientée risque |  | x | x | x | x |
| Produit | Priorisation impact vs effort |  |  | x | x | x |

## 6) Checklist d’auto-évaluation (rapide)

Tu es prêt pour un rôle "intermédiaire solide" sur ce type de projet si tu peux:
1. Implémenter un module IPC non bloquant avec tests de fragmentation.
2. Garantir un arrêt process sans fuite de ressources.
3. Diagnostiquer un bug de race condition reproductible.
4. Écrire et faire passer `ruff + mypy + pytest` en CI.
5. Expliquer clairement la frontière `core` vs `ui` et la défendre en review.

## 7) Prochaine étape concrète pour toi (dans ce repo)

1. Prendre un ticket réel "Phase 5" et rédiger un mini design (1 page).
2. Écrire 3 tests qui échouent sur un cas asynchrone réel.
3. Implémenter le correctif minimal.
4. Ajouter un test de non-régression.
5. Ouvrir une PR avec:
- contexte
- choix techniques
- risques restants
- plan de suivi.

---

Si tu veux, je peux aussi te générer une **version "roadmap personnelle 90 jours"** avec objectifs hebdo et exercices notés (débutant -> intermédiaire -> senior).
