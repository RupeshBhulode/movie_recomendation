import pandas as pd
import streamlit as st
import requests

# Your TMDB API key
TMDB_API_KEY = "8e5356dec670cfd095c4772fced85d4b"

# Load the dataset
df = pd.read_csv("BollywoodMovieD.csv")
df['actors'] = df['actors'].str.split('|')
df['genre'] = df['genre'].str.split('|')
df_exploded = df.explode('actors').explode('genre')
df_exploded['actors'] = df_exploded['actors'].str.strip()
df_exploded['genre'] = df_exploded['genre'].str.strip()

# Clean lists
all_actors = sorted([actor for actor in df_exploded['actors'].unique() if isinstance(actor, str)])
all_genres = sorted([genre for genre in df_exploded['genre'].unique() if isinstance(genre, str)])

# Recommender function
def recommend_movies_by_actor_genre(actor_name, genre_name, hitFlop=5):
    actor_movies = df_exploded[
        (df_exploded['actors'] == actor_name) &
        (df_exploded['genre'] == genre_name)
    ]
    hit_movies = actor_movies[actor_movies['hitFlop'] >= hitFlop]
    top_movies = hit_movies[['title', 'releaseYear', 'hitFlop', 'genre']].drop_duplicates()
    return top_movies.sort_values(by='hitFlop', ascending=False).head()

# Get TMDB poster URL
def get_movie_poster_url(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = data.get("results")
        if results:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for '{title}': {e}")
    return None

# Streamlit UI
st.title("🎬 Bollywood Movie Recommender")

selected_actor = st.selectbox("Choose an Actor", all_actors)
selected_genre = st.selectbox("Choose a Genre", all_genres)
min_hitFlop = st.slider("Minimum HitFlop Score", 1, 9, 5)

if st.button("Recommended Movies"):
    recommendations = recommend_movies_by_actor_genre(selected_actor, selected_genre, min_hitFlop)
    
    if not recommendations.empty:
        st.subheader("Top Recommended Movies")

        cols = st.columns(len(recommendations))

        for i, row in enumerate(recommendations.itertuples()):
            poster_url = get_movie_poster_url(row.title)
            with cols[i]:
               if poster_url:
                  st.image(poster_url, use_container_width=True, caption=row.title)
               else:
                  st.write(f"🎞️ {row.title}")
                  st.write("Poster not found")

    else:
        st.warning("No movie found with the given filters.")
