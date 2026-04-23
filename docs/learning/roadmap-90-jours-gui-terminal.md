# Roadmap 90 Jours - Software Engineer (Projet GUI Terminal)

Objectif: passer d'un niveau junior autonome a un niveau intermediaire solide sur un projet Python + GTK4 + asynchrone + IPC.

## Legende
- Charge cible: 8 a 12h / semaine
- Validation: livrable concret + commande de verification
- Niveau vise en fin de phase: N1, N2, N3 (cf. matrice de competences)

## Vue globale

| Phase | Semaines | Focus | Resultat attendu |
|---|---:|---|---|
| Phase A | 1-3 | Fondations Python, qualite, TDD | Base de code propre + tests fiables |
| Phase B | 4-6 | Asynchrone, process, IPC | Modules core robustes et testes |
| Phase C | 7-9 | GTK4/Workspace/UI states | UI stable + transitions coherentes |
| Phase D | 10-12 | Integration produit + PR quality | Feature complete prete a merge |

## Plan hebdomadaire detaille

| Semaine | Objectif principal | Exercice projet (concret) | Critere de validation |
|---:|---|---|---|
| 1 | Maitriser workflow dev | Configurer environnement, lancer `ruff`, `mypy`, `pytest` | `ruff check .`, `mypy core`, `pytest -q` passent localement |
| 2 | TDD reel | Ecrire 3 tests rouges puis implementation minimale sur un module simple | Historique git montre cycle test rouge -> vert |
| 3 | Design de code | Refactor d'un module pour clarifier API et types | Diff avec API plus explicite + tests inchanges verts |
| 4 | Event loop et non-blocking | Ecrire mini boucle GLib avec timeout/watch et test de non-blocage | Test prouve que loop reste responsive |
| 5 | Process lifecycle | Ajouter cas test stop gracieux + timeout + kill | Tests process couvrent nominal + timeout + erreur |
| 6 | IPC robuste | Ajouter tests fragmentation UTF-8 et callback fautif | Tests IPC passent sur cas limites + aucun crash |
| 7 | Bases GTK4 | Construire vue simple avec etat derive d'un modele | Test d'instanciation headless reussi |
| 8 | Workspace states | Durcir transitions Grid <-> Focus (idempotence/reentrance) | Tests UI de transitions rapides passent |
| 9 | Hygiene UI/core | Verifier separation core/ui et supprimer couplages implicites | Aucune fuite d'import core<->ui non voulue |
| 10 | Integration end-to-end | Brancher process + IPC + UI sur un flux utilisateur complet | Scenario e2e manuel documente et reproductible |
| 11 | Fiabilite production | Ajouter logs structures + gestion erreurs user-friendly | Journaux exploitables, erreurs non bloquantes |
| 12 | Delivery pro | Ouvrir PR complete (summary, risques, tests, follow-up) | PR mergeable avec checks verts |

## Rituels hebdo (simples et efficaces)

1. Lundi: definir 1 objectif technique mesurable.
2. Mercredi: revue intermediaire (tests, dette, blocages).
3. Vendredi: validation complete + notes d'apprentissage.

## Definition of Done personnelle (chaque semaine)

1. Code compile/lance sans workaround manuel.
2. Tests pertinents ajoutes (pas juste happy path).
3. Aucun warning critique ignore sans ticket.
4. Une note "ce que j'ai appris" (5 lignes minimum).

## Checkpoints de progression (J30 / J60 / J90)

| Checkpoint | Tu dois etre capable de... | Evidence demandee |
|---|---|---|
| J30 | Ajouter une feature simple en TDD sans casser le reste | 1 PR avec tests et refactor propre |
| J60 | Durcir un module asynchrone face aux erreurs/retries/timeouts | 1 batterie de tests de robustesse |
| J90 | Livrer une feature integra le core+ui avec qualite pro | PR mergeable + documentation technique claire |

## Backlog d'exercices (si tu as plus de temps)

1. Ecrire un test de race condition reproductible sur un module core.
2. Ajouter un mode "dry-run" sur ProcessManager.
3. Instrumenter un flux UI avec logs correles session/process.
4. Rediger une postmortem fictive d'un bug IPC et sa prevention.

## Commandes de validation standard

```bash
ruff check .
mypy core
xvfb-run -a pytest -q
```

## Conseils de progression rapide

1. Favorise la regularite (petits increments quotidiens) plutot que les gros sprints irréguliers.
2. Chaque bug doit produire un test de non-regression.
3. En review, argumente avec des invariants (etat, contrats, ressources), pas seulement avec "ca marche".
4. Apprends a refuser le couplage implicite tot.

---

Si tu veux, je peux te generer une version 2 avec:
- estimation de charge precise par semaine (heures par tache),
- checklist de mentoring (quand demander review, quoi demander),
- scorecard automatique (0-100) pour suivre ta progression.
