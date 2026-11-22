# UE-AD-A1-REST

Application de cinéma en micro-services réalisée pour l'UE Architectures distribuées, IMT Atlantique, FIL A1.

**Membres du groupe :** Lohan Boëglin, Rafaël Baudry

## Branches

| Branche | TP | Détails |
|---------|----|---------|
| [`rest`](https://github.com/lboeglin/UE-AD-A1-REST/tree/rest) | TP REST | Les 4 services en REST (Flask), documentés en OpenAPI |
| [`mixte`](https://github.com/lboeglin/UE-AD-A1-REST/tree/mixte) | TP MIXTE | Services REST et GraphQL, MongoDB, conteneurisation Docker |

Chaque branche a son propre README qui décrit son architecture, le lancement des services et les routes disponibles.

## Consignes (TP noté, modifications 2026-2027)

- Dockeriser l'application MIXTE
- Un service autre que Movie utilise Mongo (MIXTE)
- Rendre les TP REST et MIXTE sur Moodle (liens git)
- Écrire un README

## Ce que nous avons fait

L'application est découpée en 4 services : **Movie**, **Schedule**, **Booking** et **User**.

### TP REST (branche `rest`)

| Service  | Port | Type | Stockage |
|----------|------|------|----------|
| Movie    | 3200 | REST | JSON     |
| Booking  | 3201 | REST | JSON     |
| Schedule | 3202 | REST | JSON     |
| User     | 3203 | REST | JSON     |

- Les 4 services sont en REST (Flask) et appellent les autres avec `requests`.
- Chaque service est documenté en OpenAPI (`*.yaml`).
- Nous avons ajouté des routes qui croisent les données de plusieurs services (Movie ↔ Schedule, User ↔ Booking).

### TP MIXTE (branche `mixte`)

| Service  | Port | Type    | Stockage |
|----------|------|---------|----------|
| Movie    | 3200 | GraphQL | MongoDB  |
| Booking  | 3201 | GraphQL | JSON     |
| Schedule | 3202 | REST    | JSON     |
| User     | 3203 | REST    | JSON     |

- **Docker** : chaque service a son `Dockerfile`, et le `docker-compose.yml` lance les 4 services avec MongoDB et mongo-express (port 8081).
- **GraphQL** : Movie et Booking ont été réécrits en GraphQL (Ariadne).
- **MongoDB** : Movie stocke ses films et ses acteurs dans MongoDB.

### En plus : authentification JWT

Sur les deux branches, les services sont protégés par JWT :

- Le service User génère le token via `POST /login`. Ce token contient l'identifiant et le rôle de l'utilisateur.
- Les autres services vérifient le token, et certaines opérations sont réservées aux administrateurs.
