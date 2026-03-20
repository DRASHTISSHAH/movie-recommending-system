import os
import json
import requests
import concurrent.futures
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Fetch API key securely from environment
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")

# Load YOUR mathematically computed model from JSON!
MOVIE_DATA = {}
MOVIE_ID_MAP = {} # Allows blazing fast lookups by ID

def load_data():
    global MOVIE_DATA, MOVIE_ID_MAP
    try:
        if os.path.exists("movie_data.json"):
            with open("movie_data.json", "r") as f:
                MOVIE_DATA = json.load(f)
            # Create a reverse mapping for fast ID searches
            for title, info in MOVIE_DATA.items():
                MOVIE_ID_MAP[info["id"]] = info["similar"]
        else:
            print("Warning: movie_data.json not found! Run build_recommender.py after adding CSVs.")
    except Exception as e:
        print(f"Error loading optimized ML data: {e}")

load_data()

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/api/search", methods=["GET"])
def search_movies():
    """Live search against TMDB enabling ALL 700k+ Bollywood and Hollywood movies globally."""
    query = request.args.get("q", "")
    if not query or not TMDB_API_KEY:
        return jsonify({"results": []})
        
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US&page=1&include_adult=true"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", [])[:8]:
            results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "release_date": item.get("release_date", "")[:4] 
            })
        return jsonify({"results": results})
    except Exception as e:
        print(f"Error searching TMDB: {e}")
        return jsonify({"results": []})

def get_movie_details(rec):
    """Fetches posters and Watch Provider links synchronously per thread"""
    movie_id = rec.get("id")
    title = rec.get("title")
    
    poster_url = "/static/netflix-cover.jpg"
    watch_link = ""
    platforms = []
    
    try:
        if TMDB_API_KEY:
            # Query TMDB's Movie Poster & Details natively
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
            data = requests.get(url, timeout=3).json()
            poster_path = data.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                
            # Query TMDB's Watch Provider Endpoint
            prov_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
            prov_data = requests.get(prov_url, timeout=4).json()
            results = prov_data.get("results", {})
            
            # Prefer Indian region or generic US
            region_data = results.get("IN") or results.get("US") or {}
            
            if region_data:
                watch_link = region_data.get("link", "")
                flatrate = region_data.get("flatrate", [])
                platforms = [p.get("provider_name") for p in flatrate[:2]]
    except Exception as e:
        print(f"Details fetch failed for {movie_id}: {e}")

    return {
        "title": title,
        "poster": poster_url,
        "rating": None, 
        "overview": None,
        "watch_link": watch_link,
        "platforms": platforms
    }

@app.route("/recommend", methods=["POST"])
def get_recommendation():
    """Hybrid Recommendation Engine (Your Logic + TMDB Fallback)"""
    data = request.json
    selected_id = data.get("movie_id")
    
    if not selected_id:
        return jsonify({"error": "Invalid Movie Selected. Please try another one."}), 400
        
    recs = []
    
    # Check if the movie is inside YOUR custom Machine Learning JSON Model
    if selected_id in MOVIE_ID_MAP:
        print("Using Custom ML Logic Model!")
        recs = MOVIE_ID_MAP[selected_id][:10]
    else:
        # FALLBACK: If dataset doesn't have it (e.g., Bollywood new releases), query TMDB!
        print("Movie out of bounds. Using TMDB Live Engine!")
        if not TMDB_API_KEY:
             return jsonify({"error": "TMDB API Key missing. Please check your .env"}), 500

        url = f"https://api.themoviedb.org/3/movie/{selected_id}/recommendations?api_key={TMDB_API_KEY}&language=en-US&page=1"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            api_data = response.json()
            recs = api_data.get("results", [])[:10]
        except Exception as e:
            print(f"TMDB API Fallback Error: {e}")
            return jsonify({"error": "Failed to fetch remote recommendations."}), 500
    
    try:
        # Resolve watch providers rapidly via threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(get_movie_details, recs))
            
        if not results:
            return jsonify({"error": "No recommendations found."}), 404
            
        return jsonify({"movies": results})

    except Exception as e:
        print(f"Error fetching: {e}")
        return jsonify({"error": "Failed to map dependencies."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
