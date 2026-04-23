Rôle : Senior Software Engineer (Expert Python 3.12+, GTK4/Libadwaita, GLib async, IPC UNIX Sockets).
Mission : Implémenter la Phase 5 – Intégration Réelle & Observabilité du projet GUI Terminal. Tu dois transformer le socle durci de la Phase 4 en un orchestrateur capable de piloter de vraies instances de gemini-cli avec un monitoring professionnel.
1. Contexte Critique (À lire avant toute action)
Le projet sépare strictement le core/ (gestion processus/IPC) et l' ui/ (widgets).
•
Documents de référence : GEMINI.md, docs/superpowers/specs/2026-04-18-gemini-gui-orchestrator-design.md, et le plan de hardening de la Phase 4.
•
État actuel : ProcessManager et IpcServer sont robustes. Le Workspace gère le Focus Mode de manière responsive.
2. Objectifs Obligatoires (Phase 5)
A. Orchestration & Intégration (Fonctionnel) :
1.
Pilotage Réel : Connecter l'UI au ProcessManager pour lancer des sessions réelles (gemini-cli ou shells orchestrés).
2.
Flux IPC Inter-Agents : Implémenter la réception et le routage des messages IPC (statuts d'agents, activations de compétences) vers les composants UI dédiés.
3.
UX de Récupération : Ajouter la logique de monitoring dans l'UI pour détecter les crashs de processus et proposer un redémarrage/récupération propre.
B. Observabilité & Contrat d'Erreurs (Architecture) :
1.
Logs Structurés : Centraliser via core/logging_utils.py des logs cohérents incluant : event, session_id, pid, status, et error_code.
2.
Contrat d'Erreurs Core -> UI : Définir un format normalisé pour les erreurs (code, message amical, sévérité, contexte). Interdiction d'envoyer des stack traces brutes à l'UI.
3.
Traçabilité : Introduire un correlation_id pour suivre le cycle complet d'une requête de l'UI jusqu'au processus esclave.
3. Contraintes et Méthodologie
•
TDD Strict : AUCUN code de production sans un test qui échoue au préalable dans tests/.
•
Non-bloquant : Interdiction absolue de bloquer la boucle principale GTK. Utilise les sources GLib (io_add_watch, timeout_add).
•
Hygiène : Typage strict (mypy core/), Linting (ruff), et tests headless (xvfb-run).
•
Isolation : Travaille sur une nouvelle branche feat/phase-5-integration à partir de master.
4. Livrables Attendus
1.
Code & Tests : Implémentation complète de l'intégration et du système de logs/erreurs.
2.
Plan d'Action : Utilise le skill writing-plans pour créer docs/superpowers/plans/2026-04-20-phase5-integration-plan.md avant de coder.
3.
Documentation du Contrat d'Erreurs : Un mémo court décrivant le format JSON des erreurs échangées.
4.
Validation : Preuve d'exécution de xvfb-run -a pytest -q, mypy et ruff.
5. Commande de démarrage
"Analyse le codebase actuel sur master, crée la branche feat/phase-5-integration, et propose ton plan détaillé pour remplir les objectifs de la Phase 5."