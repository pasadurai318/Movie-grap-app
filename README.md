# Movie Graph Explorer

A movie discovery web app backed by **CognoDB** (a managed graph database), where movies and actors are connected as a graph instead of flat tables.

**Live demo:** https://movie-grap-app.onrender.com

---

## Why a graph database?

Movies and actors are naturally a network, not a set of independent rows. The core question this app answers — *"what other movies should I watch based on this one?"* — is really a **relationship** question: find movies that share actors with the movie I'm looking at.

In a relational database, this needs a many-to-many join table (`movie_actor`) and a self-join to find "other movies with the same actor," which gets slower and messier the more hops you add (e.g. "actors who worked with actors who worked with X").

In a graph database, this is a single, cheap **multi-hop traversal**:

```
(Movie) <-[:ACTED_IN]- (Actor) -[:ACTED_IN]-> (other Movie)
```

CognoDB walks the relationships directly instead of computing joins, so this stays fast even as the number of actors and movies grows, and the query itself reads like the question you're actually asking.

---

## Data model

**Nodes**
- `Movie` — `title`, `year`, `genre`, `rating`
- `Actor` — `name`

**Relationship**
- `(:Actor) -[:ACTED_IN]-> (:Movie)`

```
        ACTED_IN                 ACTED_IN
(Actor) ────────► (Movie) ◄──────────── (Actor)
   │                                        │
   └───────────────► (other Movie) ◄────────┘
              (2-hop: movies connected through a shared actor)
```

---

## Tech stack

- **Backend:** Python + Flask, official `neo4j` driver (Bolt protocol) to talk to CognoDB
- **Database:** CognoDB Cloud (free c0 instance)
- **Frontend:** Plain HTML/CSS/JS, served by Flask
- **Hosting:** Render (free web service)

---

## Setup & run locally

### 1. Create a CognoDB instance
1. Sign up at [console.cognodb.com](https://console.cognodb.com/signup) (no credit card needed).
2. Create a free (c0) instance and pick a region.
3. Copy the connection URI (`bolt+s://<instance-id>.databases.cognodb.cloud`) and the generated password for user `cognodb` — shown only once.

### 2. Configure environment variables
Create a `.env` file or set these in your shell / hosting provider:

```
COGNODB_URI=bolt+s://<your-instance-id>.databases.cognodb.com
COGNODB_USERNAME=cognodb
COGNODB_PASSWORD=<your-password>
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the database
```bash
python Seed.py
```
This clears any existing data and creates all `Movie` and `Actor` nodes plus `ACTED_IN` relationships.

### 5. Run the app
```bash
python app.py
```
Visit `http://localhost:5000`.

---

## Deployment

Hosted on Render as a free web service (see `Render.yaml`). The same `COGNODB_URI`, `COGNODB_USERNAME`, and `COGNODB_PASSWORD` environment variables are set in the Render dashboard under **Environment**.

---

## API & main queries

| Endpoint | Description |
|---|---|
| `GET /api/health` | Checks DB connectivity |
| `GET /api/genres` | Lists all distinct genres |
| `GET /api/genres/<genre>` | Movies in a genre |
| `GET /api/movies/search?q=` | Search movies by title (case-insensitive) |
| `GET /api/movies/<title>` | Movie details + cast (1-hop) |
| `GET /api/movies/<title>/similar` | **Similar movies (2-hop traversal)** — movies sharing at least one actor |
| `GET /api/actors/<name>` | Actor's filmography |

### The interesting query — similar movies (2-hop traversal)

```cypher
MATCH (m:Movie {title: $title})<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(other:Movie)
WHERE other.title <> $title
RETURN DISTINCT other.title AS title, other.year AS year,
       other.genre AS genre, other.rating AS rating,
       count(a) AS sharedActors
ORDER BY sharedActors DESC
LIMIT 6
```

This is the query a relational schema would find awkward: it needs to join `movie → movie_actor → actor → movie_actor → movie`, then group and count shared actors across that join — all parameterised here through the official driver (no string-concatenated Cypher).

---

## Error handling

If CognoDB is unreachable, all API routes catch the exception and return a JSON error with a `500` status instead of crashing, and the frontend shows a "Failed to connect to database" state instead of hanging.

---

## Screenshots

*(add screenshots of the search page, a movie's detail modal, and the similar-movies view here)*

