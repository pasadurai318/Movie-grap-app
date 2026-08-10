from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase
import os

app = Flask(_name_)
CORS(app)

URI = os.environ.get("COGNODB_URI", "bolt+s://db-09f34e9e.databases.cognodb.com")
USERNAME = os.environ.get("COGNODB_USERNAME", "cognodb")
PASSWORD = os.environ.get("COGNODB_PASSWORD", "")

def get_driver():
    return GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

@app.route("/")
def home():
    with open("index.html")as f:
    return f.read()

@app.route("/api/health")
def health():
    try:
        driver = get_driver()
        driver.verify_connectivity()
        driver.close()
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/movies/search")
def search_movies():
    query = request.args.get("q", "")
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Movie) WHERE toLower(m.title) CONTAINS toLower($query) RETURN m.title AS title, m.year AS year, m.genre AS genre, m.rating AS rating ORDER BY m.rating DESC LIMIT 10",
                query=query)
            movies = [dict(r) for r in result]
        driver.close()
        return jsonify(movies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/movies/<title>")
def movie_detail(title):
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Movie {title: $title})<-[:ACTED_IN]-(a:Actor) RETURN m.title AS title, m.year AS year, m.genre AS genre, m.rating AS rating, collect(a.name) AS actors",
                title=title)
            record = result.single()
            if not record:
                return jsonify({"error": "Movie not found"}), 404
            data = dict(record)
        driver.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/movies/<title>/similar")
def similar_movies(title):
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Movie {title: $title})<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(other:Movie) WHERE other.title <> $title RETURN DISTINCT other.title AS title, other.year AS year, other.genre AS genre, other.rating AS rating, count(a) AS sharedActors ORDER BY sharedActors DESC LIMIT 6",
                title=title)
            similar = [dict(r) for r in result]
        driver.close()
        return jsonify(similar)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/actors/<name>")
def actor_detail(name):
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (a:Actor {name: $name})-[:ACTED_IN]->(m:Movie) RETURN a.name AS actor, collect({title: m.title, year: m.year, genre: m.genre}) AS movies",
                name=name)
            record = result.single()
            if not record:
                return jsonify({"error": "Actor not found"}), 404
            data = dict(record)
        driver.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/genres")
def get_genres():
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("MATCH (m:Movie) RETURN DISTINCT m.genre AS genre ORDER BY genre")
            genres = [r["genre"] for r in result]
        driver.close()
        return jsonify(genres)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/genres/<genre>")
def movies_by_genre(genre):
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Movie {genre: $genre}) RETURN m.title AS title, m.year AS year, m.rating AS rating ORDER BY m.rating DESC",
                genre=genre)
            movies = [dict(r) for r in result]
        driver.close()
        return jsonify(movies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
