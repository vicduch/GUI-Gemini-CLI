# Phase 4 Hardening Plan - GUI Terminal

Date: 2026-04-19
Scope: `master` + `feat/phase-3-workspace`
Source: audit technique architecture/core/ui/tests

## 1. Resume executif

Le socle actuel est correct pour un prototype (IPC GLib non bloquant, separation `core/` vs `ui/`, Focus Mode fonctionnel en phase 3), mais il reste des ecarts critiques avant une phase de production:

- `ProcessManager` est un stub.
- L'IPC manque de garde-fous sur callback et certaines conditions I/O.
- Le Focus Mode est fonctionnel mais pas encore robuste/industrialise.
- Les tests existent mais ne couvrent pas les cas asynchrones difficiles (race, erreurs callback, multi-clients).

Objectif Phase 4: passer d'un prototype "qui marche" a une base fiable pour orchestration multi-processus/multi-terminaux.

## 2. Priorites de developpement

Priorite P0 (bloquant release):
- WP1 ProcessManager complet (spawn/stop/hot-reload + timeouts + signals).
- WP2 Durcissement IPC (callback safety, HUP/ERR, stop idempotent).

Priorite P1 (fortement recommande):
- WP3 Refactor Workspace Focus/Grid (etat explicite, transitions robustes).
- WP4 Renforcement tests asynchrones et IPC/UI.

Priorite P2 (qualite/maintenabilite):
- WP5 Observabilite + logs structures.
- WP6 Typage strict + outillage qualite.

## 3. Work packages detailles

### WP1 - ProcessManager production-ready (P0)

Probleme actuel:
- `core/process_manager.py` ne gere pas encore de sous-processus reels.

Travaux:
1. Implementer spawn GLib avec pipes non bloquants.
2. Introduire un modele d'etat processus par session (`starting`, `running`, `stopping`, `stopped`, `failed`).
3. Implementer arret gracieux:
   - SIGTERM
   - attente timeout configurable (ex: 3s)
   - SIGKILL si depassement.
4. Implementer hot-reload modele:
   - stop propre
   - maj commande
   - relance avec conservation `session_id`.
5. Exposer callbacks/events pour UI sans couplage direct (events neutres core).

Tests a ajouter:
1. Spawn nominal + etat `running`.
2. Stop gracieux avant timeout.
3. Stop force apres timeout.
4. Hot-reload conserve l'identite session.
5. Processus qui crash -> etat `failed` et notification.

Definition of Done:
- 100% des tests WP1 passent.
- Aucun appel bloquant dans le thread GTK.
- API `ProcessManager` documentee et typee.

### WP2 - IPC server hardening (P0)

Problemes actuels:
- `callback(msg)` non protege: une exception peut casser le flux.
- Gestion partielle des conditions I/O (`IO_HUP`, `IO_ERR`).
- Sortie debug brute dans hot path.

Travaux:
1. Encapsuler l'appel callback dans `try/except` avec remontree d'erreur controlee.
2. Gerer explicitement `GLib.IO_HUP`, `GLib.IO_ERR`, `GLib.IO_NVAL` pour cleanup fiable.
3. Remplacer `print` par logging structure.
4. Garantir `stop()` idempotent (multiple appels sans effet de bord).
5. Verifier cleanup complet socket + watches + clients sur toutes branches d'erreur.

Tests a ajouter:
1. Callback qui leve une exception (le serveur continue).
2. Client ferme brutalement (HUP) -> cleanup immediat.
3. Trames invalides UTF-8/JSON (pas de crash, serveur vivant).
4. `stop()` appele 2 fois.
5. Charge multi-clients simultanes + fragmentation croisee.

Definition of Done:
- Pas de crash serveur sur payload ou callback invalide.
- Couverture tests IPC elargie aux chemins d'erreur.

### WP3 - Workspace/Focus mode robustesse (P1)

Problemes actuels:
- Position grille stockee via attributs dynamiques sur `pane`.
- Focus "90%" base sur marges fixes, non adaptatif.
- Pas de gestion explicite de lifecycle (`remove_pane`, cleanup signaux).

Travaux:
1. Remplacer attributs dynamiques par mapping interne fort type:
   - `pane_positions: dict[TerminalPane, tuple[int, int]]`
2. Ajouter `remove_pane()` et cleanup signal handlers.
3. Stabiliser transitions `grid <-> focus`:
   - garder un etat unique source de verite.
   - ignorer transitions invalides/reentrantes.
4. Implementer dimensionnement "90%" reel (proportionnel a l'allocation disponible).
5. Preparer l'interaction "click background to unfocus" sans side effects.

Tests a ajouter:
1. Focus/unfocus rapide en boucle (pas de fuite ni duplication parent GTK).
2. Suppression d'un pane focused puis retour grid.
3. Re-focus d'un pane deja focused (idempotence).
4. Validation position d'origine apres unfocus.

Definition of Done:
- Aucun warning GTK sur reparenting/focus transitions.
- API `Workspace` explicite (`add_pane`, `remove_pane`, `focus_pane`, `unfocus_pane`).

### WP4 - TDD coverage asynchrone (P1)

Travaux:
1. Ajouter fixtures GLib/MainLoop robustes (timeouts courts + failsafe).
2. Separer tests unitaires purs et tests integration GLib/GTK.
3. Ajouter tests race-condition "best effort" reproductibles.
4. Ajouter execution headless standard (`xvfb-run`) documentee pour CI.

Objectifs minimaux de couverture:
- `core/ipc_server.py`: >= 90%
- `core/process_manager.py`: >= 90%
- `ui/views/workspace.py`: >= 80% logique (hors rendu pur)

Definition of Done:
- Suite stable sur 3 runs consecutifs (pas de flakiness observable).

### WP5 - Observabilite et erreurs (P2)

Travaux:
1. Ajouter logger central (`core.logging` ou equivalent) avec niveaux.
2. Ajouter correlation id par session/process/agent.
3. Normaliser messages erreur exploitables UI (sans stack brute).
4. Clarifier contrat d'erreurs entre core et ui.

Definition of Done:
- Logs lisibles pour diagnostiquer spawn/IPC/focus sans debugger.

### WP6 - Qualite statique et hygiene (P2)

Travaux:
1. Mypy strict sur `core/`.
2. Ruff/flake8 (selon choix projet) avec regles minimales.
3. Ajout gate CI:
   - lint
   - type-check
   - tests headless.

Definition of Done:
- Pipeline CI bloque les regressions evidentes avant merge.

## 4. Ordre de mise en oeuvre recommande

1. WP1 ProcessManager
2. WP2 IPC hardening
3. WP4 Tests async (en parallele de WP1/WP2)
4. WP3 Workspace robustesse
5. WP5 Observabilite
6. WP6 Qualite statique/CI

## 5. Criteres de sortie Phase 4

1. Tous les tests passent en headless (`xvfb-run -a pytest -q`).
2. Aucun blocage GTK detecte sur chemins critiques.
3. Hot-reload process valide sur cas nominaux + erreurs.
4. IPC resilient aux payloads fragmentes/invalides et aux callbacks fautifs.
5. Focus Mode stable sans fuite ni incoherence d'etat.

## 6. Commandes de verification

```bash
# Branche master
xvfb-run -a pytest -q

# Branche phase 3 worktree
cd ".worktrees/phase-3-workspace"
xvfb-run -a pytest -q
```

## 7. Risques residuels connus

1. Variabilite environnement GTK/VTE selon distro/display server.
2. Race conditions difficiles a reproduire a 100% en test unitaire.
3. Integration future avec vrais processus `gemini-cli` peut introduire de nouveaux cas limites IPC/process.
