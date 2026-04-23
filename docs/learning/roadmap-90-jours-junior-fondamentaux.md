# Roadmap 90 Jours - Junior Non Autonome (Socle Fondamental + Progression Projet)

Objectif: construire un socle suffisamment solide pour devenir autonome sur des tickets simples a moyens dans un projet Python + GTK4 + asynchrone.

Public cible:
- Tu connais deja la syntaxe Python.
- Tu as besoin de consolider architecture, debugging, tests, qualite, et pratique projet.

## 1) Principe de progression

Cette roadmap suit 3 niveaux:
1. **Comprendre**: savoir expliquer le "pourquoi".
2. **Reproduire**: savoir refaire avec guide.
3. **Adapter**: savoir appliquer seul sur un nouveau cas.

Regle: on ne passe au niveau suivant que si les criteres de validation sont atteints.

## 2) Cadence recommandee

- Charge: 8 a 10h/semaine
- Repartition:
  - 30% apprentissage guide
  - 50% pratique sur repo
  - 20% revue/reflexion/documentation

## 3) Plan 12 semaines (version junior guidee)

| Semaine | Focus fondamental | Exercice concret sur repo | Validation minimale |
|---:|---|---|---|
| 1 | Lire une codebase sans se perdre | Cartographier `core/`, `ui/`, `tests/` en 1 page | Tu expliques 5 flux cle (UI->core->IPC->UI) |
| 2 | Git propre et PR lisible | Faire une mini modif doc + commit propre + message clair | 1 commit propre, pas de fichiers parasites |
| 3 | Tests pytest utiles | Ajouter 2 tests sur un module existant (cas nominal + erreur) | `pytest -q` vert, tests pertinents |
| 4 | Typage et contrats | Typage strict d'une petite fonction core + test associe | `mypy core` vert, signature claire |
| 5 | Debugging structure | Reproduire un bug simple, isoler cause, proposer fix | note "symptome -> cause -> fix" |
| 6 | Asynchrone pratique | Ajouter un test timeout/retry sur logique core | test passe et ne flake pas |
| 7 | IPC robuste | Ajouter un test fragmentation ou payload invalide | serveur ne crash pas, test vert |
| 8 | Process lifecycle | Tester/ajuster stop graceful + timeout + kill | cas nominal + timeout couverts |
| 9 | UI states GTK | Ajouter test sur transition UI (focus/unfocus) | pas d'etat incoherent apres boucle rapide |
| 10 | Separation architecture | Retirer un couplage implicite core/ui (si present) | frontiere core/ui plus explicite |
| 11 | Qualite globale | Faire passer `ruff`, `mypy`, `pytest` sans aide | pipeline locale complete verte |
| 12 | Livraison complete | Ouvrir une PR complete avec resume, risques, validations | PR reviewable en une lecture |

## 4) Fondamentaux a maitriser (sans repartir de zero)

## 4.1 Architecture logicielle (essentiel)
Tu dois savoir:
- Pourquoi separer `core/` et `ui/`.
- Ce qu'est un contrat d'interface stable.
- Comment eviter les effets de bord entre couches.

Signal de maitrise:
- Tu identifies spontanement quand un widget GTK contient de la logique metier.

## 4.2 Tests (essentiel)
Tu dois savoir:
- Ecrire un test qui protege un comportement, pas une implementation fragile.
- Tester happy path + erreur + edge case.
- Rendre un test deterministic (timeouts, boucles event).

Signal de maitrise:
- Quand tu corriges un bug, tu ajoutes un test de non-regression avant/apres.

## 4.3 Asynchrone et ressources (essentiel)
Tu dois savoir:
- Pourquoi un appel bloquant casse la loop GTK.
- Comment gerer timeout, cleanup, idempotence.
- Pourquoi les fuites de fd/watchers sont dangereuses.

Signal de maitrise:
- Tu penses automatiquement "qui ferme quoi et quand ?".

## 4.4 Qualite et maintenance (essentiel)
Tu dois savoir:
- Lire une erreur `ruff` / `mypy` et la corriger proprement.
- Produire des commits petits et coherents.
- Documenter decisions et risques restants.

Signal de maitrise:
- Tes PR sont comprenables sans appel oral.

## 5) Matrice de progression junior -> autonome

| Compétence | Debut (J0) | Intermediaire (J45) | Autonome (J90) |
|---|---|---|---|
| Lire le code | Suit difficilement | Comprend un module seul | Cartographie un flux complet |
| Ecrire des tests | Happy path seulement | Ajoute erreurs simples | Couvre edge cases async |
| Debugging | Tatonne | Isole cause locale | Propose fix + test non-reg |
| Qualite | Corrige en surface | Passe lint/type avec aide | Passe gates seul |
| Architecture | Melange couches | Identifie couplages | Maintient frontieres claires |
| Livraison | Commits bruyants | Commits plus propres | PR concise et reviewable |

## 6) Routine hebdo (anti-blocage)

Chaque semaine, fais ces 5 etapes:
1. Lire un module (30 min) et resumer son role en 5 lignes.
2. Ajouter ou modifier au moins 1 test.
3. Faire 1 mini refactor sans changer le comportement.
4. Passer la trilogie qualite (`ruff`, `mypy`, `pytest`).
5. Ecrire un journal d'apprentissage (3 points):
- ce que j'ai compris,
- ce qui reste flou,
- ce que je teste la semaine suivante.

## 7) Definition of Done adaptee junior

Une tache est "finie" si:
1. Le besoin est implemente.
2. Les tests utiles existent (dont au moins 1 cas d'erreur).
3. Les checks qualite passent.
4. Le commit est propre et nomme clairement.
5. Tu peux expliquer le changement en 60 secondes.

## 8) Ressources cibles (ordre conseille)

1. pytest docs: https://docs.pytest.org/
2. mypy docs: https://mypy.readthedocs.io/
3. ruff docs: https://docs.astral.sh/ruff/
4. Python typing + asyncio docs: https://docs.python.org/3/
5. PyGObject + GTK4 docs: https://pygobject.gnome.org/ et https://docs.gtk.org/gtk4/

## 9) Scorecard simple (chaque fin de semaine)

Note de 0 a 2 sur chaque item (max 10):
- J'ai compris la logique du module travaille.
- J'ai ajoute des tests utiles.
- J'ai corrige au moins un point qualite.
- J'ai evite les regressions.
- J'ai documente ce que j'ai fait.

Interpretation:
- 0-4: renforcer fondamentaux la semaine suivante.
- 5-7: progression saine.
- 8-10: tu peux prendre un ticket plus ambitieux.

## 10) Premier objectif concret pour toi (semaine prochaine)

1. Choisir un module `core`.
2. Ajouter 2 tests:
- un nominal,
- un cas erreur/timeout.
3. Faire une petite correction ou refactor.
4. Lancer:
```bash
ruff check .
mypy core
xvfb-run -a pytest -q
```
5. Rédiger un mini compte rendu (10 lignes max).

---

Si tu veux, je peux aussi te generer une **version "planning hebdomadaire prêt à cocher"** avec taches quotidiennes (lundi -> vendredi).
