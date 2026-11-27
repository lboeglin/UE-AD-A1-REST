# UE-AD-A1-REST

Projet d'API mixtes (REST et GraphQL) en Flask réalisé pour l'UE Architectures distribuées, IMT Atlantique, FIL A1.

**Membres du groupe :** Lohan Boëglin, Rafaël Baudry

## Branches

- [`main`](https://github.com/lboeglin/UE-AD-A1-REST/tree/main) : présentation du dépôt
- [`rest`](https://github.com/lboeglin/UE-AD-A1-REST/tree/rest) : TP REST
- [`mixte`](https://github.com/lboeglin/UE-AD-A1-REST/tree/mixte) : TP MIXTE (cette branche)

## Consignes (TP MIXTE)

Voir le [sujet du TP API mixtes](https://helene-coullon.fr/pages/ue-ad-fil-25-26/tp-mixte/).

Par rapport à la branche `rest` :

- **Movie** et **Booking** sont réécrits en GraphQL. Movie gère aussi les acteurs.
- **Movie** et **User** stockent leurs données dans MongoDB. Au premier démarrage, les collections vides sont remplies à partir des fichiers `databases/*.json`.
- **Schedule** et **Booking** gardent leur base JSON.
- Les 4 services sont conteneurisés avec Docker Compose.

## Services

| Service  | Port | API | Documentation | Données |
|----------|------|-----|---------------|---------|
| Movie    | 3200 | GraphQL (`POST /graphql`) | `movie/movie.graphql` | MongoDB (base `movie`) |
| Booking  | 3201 | GraphQL (`POST /graphql`) | `booking/booking.graphql` | JSON |
| Schedule | 3202 | REST | `schedule/schedule.yaml` | JSON |
| User     | 3203 | REST | `user/user.yaml` | MongoDB (base `user`) |

Docker Compose lance aussi MongoDB (port 27017, identifiants `root` / `example`) et mongo-express pour consulter les bases (http://localhost:8081).

### Lancement avec Docker

```bash
docker compose up --build
```

### Lancement sans Docker

MongoDB doit tourner sur `localhost:27017`, par exemple avec `docker compose up mongo`. Ensuite, un terminal par service :

```bash
pip install -r requirements.txt
python movie/movie.py
python booking/booking.py
python schedule/schedule.py
python user/user.py
```

### Variables d'environnement

Elles ont toutes une valeur par défaut qui marche en local et sont réglées dans `docker-compose.yml` pour Docker.

| Variable | Services | Défaut |
|----------|----------|--------|
| `MOVIE_URL` | Booking, Schedule | `http://localhost:3200` |
| `BOOKING_URL` | User | `http://localhost:3201` |
| `SCHEDULE_URL` | Movie, Booking | `http://localhost:3202` |
| `USER_URL` | Booking | `http://localhost:3203` |
| `MONGO_URL` | Movie, User | `mongodb://root:example@localhost:27017/` |
| `JWT_SECRET` | les 4 services | clé de développement |

## Architecture

```mermaid
flowchart TD
    Client["client | admin<br/>Postman / Bruno / Insomnia<br/>Frontend"]

    User
    Booking
    Movie
    Schedule

    Client -->|REST| User
    Client -->|GraphQL| Booking
    Client -->|REST| Schedule

    Booking -->|GraphQL| Movie
    Client -->|GraphQL| Movie
    Booking -->|REST| Schedule

    User -.->|GraphQL| Booking
    Booking -.->|REST| User
    Movie -.->|REST| Schedule
    Schedule -.->|GraphQL| Movie
```

Par rapport au schéma d'origine, nous avons ajouté les flèches en pointillés :

- **Movie ↔ Schedule** : un film avec ses dates de diffusion (champ GraphQL `times` du type `Movie`, qui interroge Schedule via `GET /movies/<movieid>/times`), la suppression d'un film qui le retire aussi du programme (mutation `del_movie`, qui appelle `DELETE /movies/<movieid>/times`), et le programme d'une date avec le détail des films (`GET /times/<date>/movies`, qui interroge Movie en GraphQL).
- **User ↔ Booking** : un utilisateur avec ses réservations détaillées (`GET /users/<user_id>/bookings`, qui interroge Booking en GraphQL), et la liste des personnes ayant réservé un film (requête GraphQL `bookings_for_movie` sur Booking).

## Authentification JWT

En plus des consignes, les services sont protégés par un token JWT (HS256), aussi bien les routes REST que les requêtes GraphQL.

1. On récupère un token auprès du service User :

   ```bash
   curl -X POST http://localhost:3203/login -H "Content-Type: application/json" -d '{"user_id": "rafael_baudry"}'
   ```

2. On l'envoie ensuite dans l'en-tête de chaque requête :

   ```
   Authorization: Bearer <token>
   ```

   Exemple avec une requête GraphQL sur Booking :

   ```bash
   curl -X POST http://localhost:3201/graphql -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
     -d '{"query": "{ bookings { userid dates { date movies_details { title } } } }"}'
   ```

Le token contient l'identifiant (`sub`) et le rôle (`role`) de l'utilisateur. Il expire au bout d'une heure.

| Accès | Routes et requêtes concernées |
|-------|-------------------------------|
| Libre | Consultation des films, des acteurs, des dates de diffusion et des utilisateurs |
| L'utilisateur concerné ou un admin | Ses réservations (consultation, ajout, annulation), la modification de son profil |
| Admin uniquement | Création, modification et suppression des films, des acteurs et des dates, gestion des utilisateurs et de leur rôle, liste de toutes les réservations, réservations d'un film |
