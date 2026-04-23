# Roadmap 90 Jours - Junior Non Autonome (Version Générale Software Engineering)

Objectif: construire un socle professionnel solide pour devenir autonome sur des tâches de développement logiciel, quel que soit le stack.

Public cible:
- Tu sais déjà coder et lire du code.
- Tu manques encore d’autonomie sur design, tests, qualité, livraison et debugging.

## 1) Cadre de progression

Niveaux d’apprentissage par compétence:
1. **Comprendre**: expliquer le concept et son utilité.
2. **Appliquer avec guide**: reproduire un pattern sur un cas proche.
3. **Adapter seul**: résoudre un nouveau cas sans script détaillé.

Règle:
- Tu ne passes pas à la semaine suivante sans atteindre les validations minimales.

## 2) Charge recommandée

- 8 à 10h/semaine
- Répartition:
  - 30% théorie ciblée
  - 50% pratique
  - 20% revue/reflexion/documentation

## 3) Plan 12 semaines (général)

| Semaine | Focus fondamental | Exercice concret (générique) | Validation minimale |
|---:|---|---|---|
| 1 | Lire une codebase efficacement | Cartographier un projet: modules, flux, dépendances | Tu expliques 5 flux métier/techniques |
| 2 | Git et hygiène de travail | Faire une mini évolution avec branche + commit propre + PR | 1 PR lisible, diff limité, message clair |
| 3 | Tests utiles (pas décoratifs) | Ajouter 2 tests (nominal + erreur) sur un module existant | Test qui échoue avant fix puis passe |
| 4 | Contrats et typage | Clarifier API d’un composant (inputs/outputs/erreurs) | Type-check/lint OK, signature explicite |
| 5 | Debugging structuré | Reproduire un bug, isoler cause, proposer correctif | Note "symptôme -> cause -> fix" |
| 6 | Gestion d’erreurs et résilience | Ajouter timeout/retry/fallback sur un flux critique | Cas d’échec testé, pas de crash silencieux |
| 7 | Design modulaire | Découpler une responsabilité mal placée | Couplage réduit, comportement inchangé |
| 8 | État et transitions | Fiabiliser une logique d’état (idempotence/réentrance) | Pas d’incohérence après scénarios rapides |
| 9 | Dette technique | Refactor sécurisé d’un module dense | Diff lisible + couverture test maintenue |
| 10 | Intégration end-to-end | Relier 2-3 composants en flux complet | Scénario e2e documenté et reproductible |
| 11 | Qualité continue | Faire passer lint + type-check + tests sans aide | Pipeline locale verte 3 runs de suite |
| 12 | Livraison pro | Ouvrir une PR complète (résumé, risques, validation) | PR mergeable, feedback actionnable intégré |

## 4) Fondamentaux à maîtriser (sans repartir de zéro)

## 4.1 Architecture et découpage
Tu dois savoir:
- Définir des frontières de responsabilité.
- Limiter les dépendances croisées.
- Maintenir des interfaces stables.

Signal de maîtrise:
- Tu identifies vite les endroits où le code est trop couplé.

## 4.2 Qualité logicielle
Tu dois savoir:
- Écrire des tests qui protègent le comportement.
- Séparer test nominal, test erreur et edge case.
- Utiliser lint/type-check comme garde-fous, pas comme contrainte arbitraire.

Signal de maîtrise:
- Chaque bug corrigé produit un test de non-régression.

## 4.3 Fiabilité
Tu dois savoir:
- Gérer erreurs, timeouts, retries et idempotence.
- Nettoyer correctement les ressources.
- Penser aux cas limites avant prod.

Signal de maîtrise:
- Tu anticipes les pannes plutôt que réagir après coup.

## 4.4 Delivery et collaboration
Tu dois savoir:
- Faire des commits atomiques et explicites.
- Ouvrir des PR reviewables rapidement.
- Documenter choix techniques et risques résiduels.

Signal de maîtrise:
- Tes changements sont compréhensibles sans contexte oral.

## 5) Matrice de progression junior -> autonome

| Compétence | Début (J0) | Intermédiaire (J45) | Autonome (J90) |
|---|---|---|---|
| Lecture codebase | Compréhension locale | Compréhension module | Compréhension flux complet |
| Tests | Happy path | Erreurs simples | Edge cases + non-régression |
| Debugging | Tâtonnement | Cause locale identifiée | Diagnostic systémique |
| Design | Patch direct | Découpage guidé | Découpage pertinent autonome |
| Qualité | Corrige lint ponctuellement | Passe checks avec aide | Passe tous checks seul |
| Livraison | Commits flous | Commits plus ciblés | PR claire, défendable, mergeable |

## 6) Routine hebdo anti-blocage

1. Lire 1 module et résumer son rôle (15-30 min).
2. Ajouter/adapter au moins 1 test utile.
3. Faire 1 mini refactor sans changer le comportement.
4. Lancer la trilogie qualité du projet.
5. Écrire un journal d’apprentissage (3 points):
- ce que j’ai compris,
- ce qui est encore flou,
- ce que je teste la semaine prochaine.

## 7) Definition of Done (adaptée junior)

Une tâche est "finie" si:
1. Le besoin est implémenté.
2. Les tests couvrent nominal + au moins 1 erreur.
3. Les checks qualité passent.
4. Le commit est propre et ciblé.
5. Tu peux expliquer le changement en 60 secondes.

## 8) Scorecard hebdo (0 à 10)

Mets 0, 1 ou 2 sur chaque item:
1. J’ai compris la logique du composant travaillé.
2. J’ai ajouté des tests réellement utiles.
3. J’ai traité au moins un point de qualité.
4. Je n’ai pas introduit de régression.
5. J’ai documenté clairement ce que j’ai fait.

Interprétation:
- 0-4: renforcer fondamentaux
- 5-7: progression saine
- 8-10: prêt pour ticket plus ambitieux

## 9) Ressources universelles (ordre conseillé)

1. Documentation officielle de ton langage principal
2. Documentation de ton framework de tests
3. Outil de type-check du langage
4. Outil de lint/qualité
5. Références d’architecture logicielle (Clean Architecture, Refactoring, etc.)

## 10) Premier sprint conseillé (7 jours)

1. Choisir un module existant d’un projet.
2. Écrire 2 tests (nominal + erreur).
3. Corriger/refactor une petite zone fragile.
4. Passer toutes les validations locales.
5. Ouvrir une PR avec:
- résumé,
- décisions techniques,
- risques résiduels,
- commandes de validation.

---

Si tu veux, je peux te générer une **version personnalisée à ton stack exact** (backend web, mobile, data, embarqué, etc.) avec objectifs et exercices adaptés.
