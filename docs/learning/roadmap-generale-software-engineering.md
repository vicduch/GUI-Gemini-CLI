# Roadmap Générale - Apprendre le Software Development / Engineering

Objectif: devenir un développeur logiciel solide, capable de concevoir, implémenter, tester, livrer et maintenir des systèmes fiables.

Public cible:
- Tu sais déjà coder.
- Tu veux progresser vers une pratique professionnelle de l’ingénierie logicielle.

## 1) Vision d’ensemble

Le software engineering, ce n’est pas seulement "écrire du code", c’est maîtriser 6 dimensions:
1. **Code**: lisible, testable, maintenable.
2. **Design**: architecture, interfaces, découpage.
3. **Qualité**: tests, types, lint, revues.
4. **Livraison**: Git, CI/CD, versioning, release.
5. **Opérations**: logs, monitoring, debugging prod.
6. **Collaboration**: communication, specs, PR, documentation.

## 2) Plan 6 mois (24 semaines)

## Phase A (Semaines 1-4) - Fondations pro

Objectif: passer de "je code" à "je livre du code propre".

Compétences:
- Git propre (branches, commits atomiques, PRs claires)
- Qualité locale (formatter/linter/type checker)
- Tests unitaires de base
- Debugging structuré

Livrables:
- 2 mini projets avec tests
- 1 PR "propre" (description, risques, validation)

Validation:
- Tu peux expliquer chaque changement et sa couverture test.

## Phase B (Semaines 5-8) - Conception logicielle

Objectif: savoir structurer un projet avant de coder.

Compétences:
- SOLID (pragmatique), séparation des responsabilités
- API design (inputs/outputs/erreurs)
- Refactoring sûr
- Modélisation simple (diagramme flux/dépendances)

Livrables:
- Refactor d’un module avec même comportement
- Design doc court (1-2 pages) avant implémentation

Validation:
- Couplage réduit, code plus lisible, tests inchangés/renforcés.

## Phase C (Semaines 9-12) - Fiabilité et asynchrone

Objectif: gérer les cas réels difficiles.

Compétences:
- Timeouts, retries, idempotence
- Gestion d’erreurs robuste
- Concurrence/asynchronisme (niveau pratique)
- Nettoyage des ressources

Livrables:
- 1 module résilient (avec tests d’erreurs)
- 1 postmortem simulée d’un bug de prod

Validation:
- Tu sais anticiper les pannes, pas seulement les corriger.

## Phase D (Semaines 13-16) - Data, persistance, interfaces

Objectif: construire des systèmes complets.

Compétences:
- Modèles de données, migrations, validation
- Contrats API (REST/gRPC/event-driven concepts)
- Caching basique et cohérence
- Gestion des versions de schéma/API

Livrables:
- 1 service CRUD bien testé + migrations
- 1 contrat API documenté

Validation:
- Le service évolue sans casser ses clients.

## Phase E (Semaines 17-20) - Livraison et production

Objectif: comprendre la vie du code après merge.

Compétences:
- CI/CD pipelines
- Versioning, changelog, release
- Observabilité (logs, métriques, traces)
- Alerting et debugging production

Livrables:
- Pipeline CI complet sur un projet
- Dashboard/logs exploitables pour diagnostiquer un incident

Validation:
- Tu peux diagnostiquer un incident sans debugger local.

## Phase F (Semaines 21-24) - Niveau ingénierie

Objectif: passer au niveau "propriétaire de système".

Compétences:
- Arbitrages techniques (performance, dette, délai)
- Sécurité pratique (secrets, auth, permissions)
- Collaboration inter-équipe
- Mentorat/review structurée

Livrables:
- 1 projet intégrateur (de la spec à la release)
- 1 revue technique écrite de niveau senior

Validation:
- Tu proposes des solutions défendables avec trade-offs explicites.

## 3) Routine hebdomadaire recommandée

1. **Plan (1h)**: objectif mesurable de la semaine.
2. **Build (4-6h)**: implémentation en petits incréments.
3. **Test (2-3h)**: happy path + erreurs + edge cases.
4. **Review (1h)**: auto-review et dette technique.
5. **Learning note (30min)**: ce que tu as appris et ce qui reste flou.

## 4) Matrice de compétences (générale)

Niveaux:
- N1: junior guidé
- N2: autonome
- N3: confirmé
- N4: senior

| Domaine | N1 | N2 | N3 | N4 |
|---|---:|---:|---:|---:|
| Git / PR | x | x | x | x |
| Tests unitaires | x | x | x | x |
| Tests intégration |  | x | x | x |
| Typage / lint | x | x | x | x |
| Design modulaire |  | x | x | x |
| Refactoring sûr |  | x | x | x |
| Asynchrone / concurrence |  |  | x | x |
| Résilience (timeouts/retries) |  |  | x | x |
| API / contrats |  | x | x | x |
| CI/CD |  | x | x | x |
| Observabilité |  |  | x | x |
| Sécurité pratique |  |  | x | x |
| Leadership technique |  |  |  | x |

## 5) Ressources prioritaires

Fondamentaux:
- The Pragmatic Programmer
- Clean Architecture
- Refactoring (Fowler)

Qualité:
- Documentation officielle de ton langage + tests + lint + type checker
- Test Pyramid (Martin Fowler)

Architecture et systèmes:
- Designing Data-Intensive Applications
- Release It!

Production/SRE:
- Google SRE Book

## 6) Scorecard mensuelle (auto-évaluation)

Note de 0 à 2 par item (max 20):
1. Je livre des PRs claires et testées.
2. Je sais diagnostiquer un bug sans hasard.
3. Je maîtrise les erreurs et cas limites.
4. Je conçois avant de coder les parties complexes.
5. Je réduis la dette au lieu d’en créer.
6. Je comprends l’impact prod de mes choix.
7. Je documente mes décisions techniques.
8. Je collabore efficacement en review.
9. Je respecte les standards qualité.
10. Je peux expliquer mes trade-offs.

Interprétation:
- 0-8: socle à renforcer
- 9-14: progression solide
- 15-20: niveau confirmé en construction

## 7) Comment utiliser cette roadmap

1. Choisir 1 phase active à la fois.
2. Définir 1 livrable concret/semaine.
3. Mesurer (tests, CI, qualité, feedback review).
4. Réviser tous les 30 jours:
- ce qui progresse,
- ce qui bloque,
- ce qu’il faut simplifier.

---

Si tu veux, je peux te générer une **version personnalisée à ton niveau actuel** (avec planning hebdo précis, exercices et critères de passage N1 -> N2).
