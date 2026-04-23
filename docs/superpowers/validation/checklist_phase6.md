    # Checklist de Tests - GUI Terminal (Phase 6)

Ce document récapitule les tests manuels à effectuer pour valider la stabilité et les fonctionnalités de l'application après l'implémentation de la Phase 6.

## 1. Initialisation et Interface de Base
- [ ] **Lancement** : Exécuter `python main.py`. L'application s'ouvre sans erreur dans la console.
- [ ] **Rendu Libadwaita** : Vérifier que l'interface utilise les widgets Libadwaita (coins arrondis, HeaderBar intégrée).
- [ ] **Taille initiale** : La fenêtre s'ouvre à une taille raisonnable (1200x800).

## 2. Workspace et Mode Focus
- [ ] **Grille** : Un terminal est présent par défaut au centre.
- [ ] **Zoom** : Cliquer sur l'icône "Agrandir" (loupe/fullscreen) d'un terminal. Le mode Focus s'active.
- [ ] **Transition** : Le passage de la Grille au Focus utilise une transition fluide (Crossfade).
- [ ] **Désactivation Focus** : Cliquer dans la zone vide autour du terminal focalisé pour revenir à la grille.
- [ ] **Responsive** : Redimensionner la fenêtre principale ; le terminal doit s'adapter sans bug.

## 3. Navigation Latérale (Barre Gauche)
- [ ] **Navigation** : Cliquer sur l'icône "Skills" dans l'en-tête de la barre gauche. La vue bascule sur "Skills".
- [ ] **Retour** : Cliquer sur le bouton "Retour" (<) pour revenir à la vue "History".
- [ ] **Contenu** : Vérifier la présence des éléments d'exemple (Session 1, Session 2, Skill Creator).
- [ ] **Largeur** : La barre gauche doit rester à 250px de large.

## 4. Paramètres et Thématisation
- [ ] **Ouverture** : Cliquer sur l'icône "Engrenage" dans la barre d'en-tête. La fenêtre des réglages s'affiche.
- [ ] **Thème Manuel** : Sélectionner "Dark". L'application doit passer instantanément en mode sombre.
- [ ] **Thème Système** : Sélectionner "System". L'application doit suivre le thème global de GNOME.
- [ ] **Persistance** : Fermer l'application en mode sombre. La réouvrir : elle doit être encore en mode sombre.
- [ ] **API Key** : Saisir une valeur dans le champ API Key, fermer, et vérifier que la valeur est stockée dans `~/.config/gemini-gui/config.json`.

## 5. Hot-Reload du Modèle
- [ ] **Changement de modèle** : Sélectionner "gemini-1.5-flash" dans le menu déroulant central.
- [ ] **Logs** : Vérifier dans la console le message : `Restarting session 'default' with model gemini-1.5-flash`.
- [ ] **Relance** : Le processus lié au terminal doit être tué et relancé avec le nouveau paramètre `--model`.

## 6. Monitoring des Agents (Barre Droite)
- [ ] **Visibilité** : La barre droite doit être visible et afficher les agents.
- [ ] **Test IPC** : (Optionnel) Simuler un message IPC pour voir un agent s'ajouter :
  `echo '{"agent_id": "test", "status": "running"}' | socat - UNIX-CONNECT:/tmp/gemini-gui-ipc.sock`

## 7. Robustesse
- [ ] **Bannière d'erreur** : Simuler un crash (ex: `kill` sur le processus CLI). Une bannière d'erreur rouge doit apparaître en haut du terminal.
- [ ] **Config Manager** : Supprimer le fichier `config.json` et relancer l'app. Elle doit recréer une config par défaut proprement.
