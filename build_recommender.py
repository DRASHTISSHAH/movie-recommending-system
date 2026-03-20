import pandas as pd
import ast
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def convert(text):
    L = []
    try:
        for i in ast.literal_eval(text):
            L.append(i['name']) 
        return L
    except:
        return []

def convert3(text):
    L = []
    counter = 0
    try:
        for i in ast.literal_eval(text):
            if counter < 3:
                L.append(i['name'])
            counter+=1
        return L
    except:
        return []

def fetch_director(text):
    L = []
    try:
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                L.append(i['name'])
                break
        return L
    except:
        return []

print("Loading Data (Please ensure tmdb_5000_movies.csv and tmdb_5000_credits.csv are in the folder)...")
try:
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
except FileNotFoundError:
    print("Dataset not found! Please place tmdb_5000_movies.csv and tmdb_5000_credits.csv back in the folder.")
    exit()

movies = movies.merge(credits, on='title')
movies = movies[['movie_id','title','overview','genres','keywords','cast','crew','vote_average']]
movies.dropna(inplace=True)

print("Processing Deep Learning Tags...")
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)

movies['overview'] = movies['overview'].apply(lambda x:x.split())
movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ","") for i in x])
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

new_df = movies[['movie_id','title','tags','vote_average']]
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())

print("Calculating Mathematical Similarity (CountVectorizer Cosine Distances)...")
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

print("Exporting mathematically optimized dataset to JSON...")
movie_database = {}

for i in range(len(new_df)):
    distances = similarity[i]
    movie_id = int(new_df.iloc[i].movie_id)
    title = new_df.iloc[i].title
    vote_avg = float(new_df.iloc[i].vote_average)
    
    # Store top 15 similarities directly generated via your matrix logic 
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:16]
    
    similar_movies = []
    for idx, _ in movie_indices:
        similar_movies.append({
            "id": int(new_df.iloc[idx].movie_id),
            "title": new_df.iloc[idx].title
        })

    movie_database[title] = {
        "id": movie_id,
        "rating": vote_avg,
        "similar": similar_movies
    }

with open('movie_data.json', 'w') as f:
    json.dump(movie_database, f)

print("Done! Optimization complete. Created movie_data.json to act as your model's neural schema.")
