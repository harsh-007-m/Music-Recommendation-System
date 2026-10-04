from pathlib import Path
import numpy as np
import pandas as pd
from rapidfuzz import process, fuzz

DATA = Path(__file__).parent / "data"
df = pd.read_csv(DATA / "spotify_tracks_final.csv")
df["_title"] = df["_title"].fillna("").astype(str)
df["_artist"] = df["_artist"].fillna("").astype(str)
X = np.load(DATA / "X_scaled.npy")
assert len(df) == len(X)

REGIONAL = {"indian", "pop-film", "k-pop", "j-pop", "j-rock", "j-idol", "j-dance",
            "mandopop", "cantopop", "anime", "latin", "latino", "brazil", "samba",
            "pagode", "sertanejo", "mpb", "forro", "turkish", "malay", "iranian",
            "german", "french", "spanish", "swedish", "salsa", "tango", "reggaeton"}

df["_regional"] = df["all_genres"].fillna("").apply(
    lambda g: bool(REGIONAL & set(g.split(", ")))
)
df["_primary"] = df["_artist"].str.split(";").str[0].str.strip()

df["_regional"] |= df["track_name"].str.contains(r'(?:\(|-\s*)From\s+"', na=False, regex=True)

BLOCK_ARTISTS = {"sachet tandon", "karan aujla"}
df["_regional"] |= df["_artist"].apply(
    lambda a: any(x.strip() in BLOCK_ARTISTS for x in a.split(";"))
)

# propagate: an artist with mostly regional tracks is regional everywhere
ex = df[["_artist", "_regional"]].copy()
ex["_artist"] = ex["_artist"].str.split(";")
ex = ex.explode("_artist")
share = ex.groupby("_artist")["_regional"].mean()
regional_artists = set(share[share >= 0.5].index)

df["_regional"] |= df["_artist"].apply(
    lambda a: any(x in regional_artists for x in a.split(";"))
)

def find_song(title, artist=None):
    pool = df
    if artist:
        pool = df[df["_artist"].str.contains(artist.lower().strip(), regex=False)]
    if pool.empty:
        return None
    hit = process.extractOne(title.lower().strip(), pool["_title"],
                             scorer=fuzz.WRatio, score_cutoff=85)
    if hit is None:
        return None
    rows = pool[pool["_title"] == hit[0]]
    return rows["popularity"].idxmax()


def recommend(title, artist=None, n=5, min_pop=50):
    """Returns (matched_song_row, recommendations_df), or (None, None)."""
    pos = find_song(title, artist)
    if pos is None:
        return None, None
    q = df.loc[pos]
    genres = q["all_genres"].split(", ")

    mask = (df["track_genre"].isin(genres)
            & (df["popularity"] >= min_pop)
            & (df.index != pos)
            & (df["_primary"] != q["_primary"]))
    if not q["_regional"]:
        mask &= ~df["_regional"]
    sub = df[mask].copy()
    if sub.empty:
        return q, None

    d = np.linalg.norm(X[sub.index] - X[pos], axis=1)
    sub["audio_sim"] = 1 / (1 + d)
    sub["score"] = sub["audio_sim"] + 0.1 * sub["popularity"] / 100

    sub["_base"] = sub["_title"].str.replace(r"\s+-\s+.*$", "", regex=True).str.strip()
    sub = sub.sort_values("score", ascending=False)
    sub = sub.drop_duplicates("_base").groupby("_primary", sort=False).head(1).head(n)
    return q, sub[["track_id", "track_name", "artists", "track_genre",
                   "popularity", "audio_sim"]]