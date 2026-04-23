# 📄 DOCUMENT DE SPÉCIFICATIONS TECHNIQUES (PRD) - IA AGENT PROMPT
**Projet :** Gemini CLI - GUI Wrapper & Orchestrator
**Date cible :** Avril 2026
**Environnement cible :** Fedora Linux 44, Wayland, GNOME 50

## 1. CONTEXTE ET OBJECTIF
Agis en tant que développeur Python/GTK4 expert sous l'écosystème Linux GNOME. L'objectif est de développer une application graphique (GUI) servant de "Tour de contrôle" et de multiplexeur pour un outil en ligne de commande (Gemini CLI). L'application doit permettre la gestion visuelle des historiques, l'orchestration dynamique des modèles (Génération Gemini 3.x), le monitoring en temps réel de sous-agents (Agentic Swarm), et un système de fenêtrage de terminaux embarqués avec "Focus Mode".

## 2. STACK TECHNIQUE SÉLECTIONNÉE
*   **Langage :** Python 3.12+
*   **Interface Graphique (Toolkit) :** GTK4 avec Libadwaita (via `PyGObject`).
*   **Émulateur de Terminal :** `Vte.Terminal` (Virtual Terminal Emulator de GNOME) pour embarquer les terminaux nativement dans la GUI.
*   **Système de fenêtrage :** Wayland (Standard sur Fedora).
*   **Communication Inter-Processus (IPC) :** Sockets Unix (ex: `/tmp/gemini-gui.sock`) pour la communication asynchrone entre le CLI et la GUI.

## 3. FONCTIONNALITÉS PRINCIPALES (LES 6 PILIERS)

### Pilier A : Gestionnaire d'Historique et Espaces de Travail
*   **Interface :** Affichage en Grille (Cards) des anciennes sessions.
*   **Organisation :** Tri automatique par "Espace de travail" (basé sur le dossier d'exécution, ex: `~/Projets/AppWeb`).
*   **Données :** Lecture des métadonnées locales du CLI (`~/.local/share/gemini-cli/sessions/`).
*   **Aperçu rapide (Preview) :** Au survol d'une carte de la grille, afficher le premier message ou un résumé généré automatiquement du contexte de la discussion.
*   **Action :** Le clic sur une carte génère la commande de reprise et lance le terminal cible embarqué (`gemini-cli --resume <session_id>`).
 *   **Recherche Globale :** Une barre de recherche "Full-text" pour retrouver une discussion contenant un mot précis parmi tous les historiques.
### Pilier B : Sélecteur Dynamique de Modèles & Hot-Reload
*   **Modèles pris en charge (2026) :** Gemini 3 Flash (Vitesse), Gemini 3.1 Pro (Raisonnement), Gemini 3.1 Flash Lite (Léger) et modèle locaux Gemma 4 via LMStudio et Ollama. 
*   **Action UI :** Badge interactif sur chaque carte pour changer le modèle via un menu déroulant (`Gtk.DropDown`).
*   **Hot-Reload :** Possibilité de changer de modèle ou de température *pendant* qu'une session tourne. La GUI envoie un signal de sauvegarde, tue le processus, et le relance instantanément avec les nouveaux arguments (`--resume <ID> --model gemini-3.1-pro`).

### Pilier C : Hub d'Extensions (Skills) et Paramètres
*   **Contrôles :** *Switchs* (Boutons bascules GTK) pour activer/désactiver les skills (Web, Filesystem, Code) avant de lancer la session.
*   **Formulaires :** Panneau latéral de configuration pour renseigner les clés API ou variables d'environnement.
*   **Gestionnaire de Paquets interne :** Une vue claire avec deux onglets : "Installés" et "Découverte" (pour télécharger de nouvelles skills).

### Pilier D : Moteur de Thèmes et Intégration GNOME
*   **Synchronisation Système :** Utilisation de l'API Libadwaita (`Adw.StyleManager`) pour un basculement automatique du thème de l'app selon le mode Clair/Sombre de GNOME 50.
*   **Thèmes Contextuels :** Application de couleurs spécifiques au terminal VTE selon le contexte (Rouge = Root, Bleu = Dev).
*   **Profils de thèmes :** Créer des thèmes (couleur des prompts, de l'assistant, syntax highlighting) et les injecter dynamiquement.

### Pilier E : Moniteur de Sous-Agents (Agentic Swarm)
*   **Concept :** Le CLI Gemini peut générer des sous-agents en parallèle. La GUI doit visualiser cela en temps réel via IPC.
*   **Mécanisme IPC :** Le CLI envoie des évènements JSON via un Unix Socket (`{"session_id": "123", "event": "spawn", "agent_id": "alpha_1", "status": "running"}`).
*   **Interface (Tree View) :** Vue en arborescence de la session active montrant le "Master Agent" et ses sous-agents. Boutons d'action pour envoyer un signal "KILL" ou "PAUSE" à un sous-agent spécifique.

### Pilier F : Multiplexeur de Terminaux Universel et "Focus Mode"
*   **Agnosticité :** L'application est un multiplexeur (Tiling Terminal). L'utilisateur peut diviser l'écran pour afficher plusieurs terminaux simultanément (ex: grille 2x2 avec 4 terminaux), qu'il s'agisse de sous-agents IA ou de simples terminaux Bash/Zsh.
*   **Composant `TerminalPane` :** Chaque terminal est un `Gtk.Overlay` encapsulant un `Vte.Terminal`. L'overlay contient un bouton (Zoom ⛶) superposé discrètement en haut à droite.
*   **Layout en Grille :** Les `TerminalPane` sont organisés dynamiquement dans un `Gtk.Grid`.
*   **Focus Mode (Zoom) :** 
    *   Au clic sur le bouton ⛶ d'un `TerminalPane`, l'application utilise un `Gtk.Stack` (transition: `ZOOM`) pour masquer le `Gtk.Grid` et afficher uniquement ce `TerminalPane` en plein écran dans la fenêtre.
    *   Le bouton devient un bouton "Retour" 🔙 (ou la `Adw.HeaderBar` affiche un bouton de retour) pour restaurer la grille 2x2.

## 4. ARCHITECTURE DU PROJET ATTENDUE
Instructions : Cette architecture est une proposition. Tu dois étudier cette architecture, et la remttre en question et l'améliorer si nécessaire. 
```text
gemini-gui-orchestrator/
│
├── main.py                   # Point d'entrée (Adw.Application)
├── core/
│   ├── session_manager.py    # Gestion des JSON d'historique
│   └── ipc_server.py         # Serveur Unix Socket (asyncio) pour écouter les events des agents
│
├── ui/
│   ├── window.py             # Fenêtre principale (Adw.ApplicationWindow)
│   ├── session_grid.py       # Vue des anciennes sessions avec badges de modèles
│   ├── settings_panel.py     # Panneau des Skills
│   ├── agent_monitor.py      # TreeView dynamique des sous-agents
│   ├── terminal_pane.py      # Composant Gtk.Overlay + Vte.Terminal + Bouton Zoom
│   └── terminal_grid.py      # Gtk.Grid (2x2) + Gtk.Stack pour le Focus Mode
│
├── assets/
│   └── style.css             # CSS personnalisé (Libadwaita overrides)
│
└── requirements.txt          # PyGObject, etc.
