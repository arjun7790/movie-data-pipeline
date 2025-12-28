import pandas as pd
import pymysql
import requests
import time

API_KEY = "1c5777b9"

# DB connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="moviedb",
    port=3306
)
cursor = conn.cursor()

# Read CSV files
movies_df = pd.read_csv("data/movies.csv")
ratings_df = pd.read_csv("data/ratings.csv")

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("Response") == "True":
            return res
    except Exception:
        pass
    return None

def clean_box_office(value):
    if value and value != "N/A":
        return int(value.replace("$", "").replace(",", ""))
    return None

# Load Movies + Genres
for _, row in movies_df.iterrows():
    movie_id = int(row["movieId"])
    title = row["title"]
    genres = row["genres"].split("|")

    api_data = fetch_omdb(title)
    director = api_data.get("Director") if api_data else None
    plot = api_data.get("Plot") if api_data else None
    year = api_data.get("Year") if api_data else None
    box_office = clean_box_office(api_data.get("BoxOffice")) if api_data else None

    cursor.execute("""
        INSERT IGNORE INTO movies
        (movie_id, title, year, director, plot, box_office)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (movie_id, title, year, director, plot, box_office))

    for genre in genres:
        cursor.execute(
            "INSERT IGNORE INTO genres (genre_name) VALUES (%s)", (genre,)
        )
        cursor.execute(
            "SELECT genre_id FROM genres WHERE genre_name = %s", (genre,)
        )
        genre_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT IGNORE INTO movie_genres (movie_id, genre_id)
            VALUES (%s, %s)
        """, (movie_id, genre_id))

    time.sleep(0.2)  # API rate limit

# Load Ratings
for _, row in ratings_df.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO ratings
        (user_id, movie_id, rating, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (
        int(row["userId"]),
        int(row["movieId"]),
        float(row["rating"]),
        int(row["timestamp"])
    ))

conn.commit()
conn.close()

print("ETL completed successfully")
