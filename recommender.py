import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("C:/Users/HARSHITA/OneDrive/Desktop/music/data/spotify-tracks-dataset-detailed.csv")

features = [
    "danceability","energy","acousticness","instrumentalness","liveness","speechiness","valence","tempo","loudness"
]

X = df[features].fillna(0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

knn = NearestNeighbors(
    n_neighbors=6,
    metric ="cosine"
)

knn.fit(X_scaled)

def recommend(song_name, n=5):
    matches = df[
        df["track_name"].str.lower() == song_name.lower()
    ]

    if matches.empty:
        return None

    song_index = matches.index[0]
    song_vector = X_scaled[song_index].reshape(1, -1)

    # Find nearest neighbors
    distances, indices = knn.kneighbors(
        song_vector,
        n_neighbors=n + 1
    )

    # First result is the song itself, so remove it
    recommended_indices = indices[0][1:]

    recommendations = df.iloc[recommended_indices][
        ["track_name", "artists", "track_genre"] + features
    ].copy()

    # Convert cosine distance to cosine similarity
    recommendations["similarity"] = (
        1 - distances[0][1:]
    )

    print(recommendations.to_string(index=False))

if __name__ == "__main__":
    result = recommend("Blinding Lights")

    if result is not None:
        print(result.to_string(index=False))
    else:
        print("Song not Found")

    song = df[df["track_name"].str.lower() == "blinding lights"].iloc[0]

    print("\nBlinding Lights features:")
    print(song[features])