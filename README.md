# Advanced Movie Recommender System

An advanced, highly-optimized Movie Recommendation System powered by Machine Learning and Flask.

## Features & Optimizations

- **Vercel & Heroku Ready**: The application is 100% serverless with zero static dataset dependencies.
- **Infinite Library**: By connecting directly to TMDB's live `/search` and `/recommendations` API endpoints, you instantly have access to every Bollywood, Hollywood, and newly-released film globally without having to update static datasets or CSVs!
- **Decoupled API Key**: TMDB API key is injected directly from local environment variables keeping source-code completely secure.

## How It Works
The application uses the user's provided TMDB API Key to dynamically live query the entire global dataset. The front-end leverages advanced JavaScript async fetches to live-populate search matches, and seamlessly fetches AI-driven real-time matches from TMDB's core recommendation algorithms.

## Local Setup

**1. Create a modern Python Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

**2. Install Fast Loading Prerequisites**
```sh
pip install -r requirements.txt
```

**3. Setup Environment Variable**
Please copy `.env.example` to `.env` and assign your exact TMDB API Token.
```sh
cp .env.example .env
```

**4. Start Server**
```sh
python app.py
```
Open up your browser to `http://localhost:5000` to execute testing locally.

## Deploying on Vercel
Thanks to the configured `vercel.json` runtime manifest, you securely push this exact repository to any blank GitHub repository and instantly link it with a new Vercel application. Add your `TMDB_API_KEY` into your Vercel Dashboard configurations.

## Deploying on Heroku
Alternatively, standard `REQUIREMENTS` and Flask components effectively enable standard Heroku deployments seamlessly via standard git deployment hooks. Add your `TMDB_API_KEY` via `Settings -> Config Vars`.
