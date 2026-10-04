# 🎧 Music Recommender

Type a song you like and get five others that sound similar. A content-based recommender built on Spotify audio features, with a Streamlit interface.

**Live demo:** _https://bro-recommend-a-song.streamlit.app/

## What it does

- Finds your song with fuzzy matching, so small typos still work, and accepts an optional artist to pick the right version of a common title.
- Recommends five songs from the same genre that match its tempo, energy, mood and acoustic character, using only well-known tracks.
- Shows one song per artist, with a generated cover and a link that opens each track on Spotify.

## How it works

1. **Match the song.** The input is compared against about 79,000 cleaned titles. If several songs share a title, the most popular one wins unless an artist is given.
2. **Pick candidates.** Only songs that share a genre with the input and have a popularity of at least 50.
3. **Rank by sound.** Each candidate is scored by its Euclidean distance to the input across 12 audio features, converted to a similarity of `1 / (1 + distance)`, with a small popularity bonus (`0.1 × popularity / 100`).
4. **Tidy the list.** One result per artist (collaborations count under the first-listed artist), alternate versions of the same song collapsed, and regional or non-English songs removed unless the input song is regional itself.

### Audio features

`danceability`, `energy`, `acousticness`, `instrumentalness`, `liveness`, `speechiness`, `valence`, `tempo`, `loudness`, `mode`, and `key`, encoded as `key_sin` / `key_cos` because pitch class is circular.

Before comparison, `speechiness` and `liveness` are log-transformed, tiny `instrumentalness` values are zeroed, and `loudness` is clipped at -25 dB. Everything is then standardized and weighted. Features that describe how a song feels (energy, danceability, acousticness, valence, instrumentalness) get the highest weights, while `key` and `mode` get the lowest.

## Design decisions

- **Genre first, then distance.** The first version used k-nearest-neighbors with cosine distance over the whole catalog. It found songs that sounded alike but came from unrelated genres (a synth-pop track matched drum-and-bass and show tunes). Filtering by genre first fixed that, and the remaining set is small enough to compute exact distances directly, so scikit-learn isn't needed at runtime.
- **Euclidean over cosine.** After standardizing, cosine only compares the direction of a song's deviation from average, while Euclidean also respects how far apart two songs are.
- **Dedupe aggressively.** The raw data lists the same track once per genre, plus remasters and re-releases. Without dedupe, a song's closest neighbors were its own copies.

## Results

I judged the output by ear on five seed songs across pop, rap, rock, ballads and indie, rating each of the 25 recommendations as a good or poor fit for a shared playlist. About 22 of 25 fit. This is an informal check and not a benchmark. The misses were mainly non-English songs that the genre tags couldn't separate from English-language ones.

## Project structure

```
Music-Recommendation-System/
├── app.py                  # Streamlit interface
├── recommender.py          # search, filtering and ranking logic
├── requirements.txt
├── .streamlit/
│   └── config.toml         # theme
├── data/
│   ├── spotify_tracks_final.csv   # cleaned catalog (~79k tracks)
│   └── X_scaled.npy               # transformed, weighted feature matrix
└── notebooks/
    ├── 01_data_preprocessing.ipynb
    ├── 02_transforming.ipynb
    └── 03_testing_recommender.ipynb
```

## Limitations

- **Sound is not taste.** Audio features can't see lyrics, era, language or what listeners play together, so some matches sound similar without belonging on one playlist.
- **No language column.** The dataset's `pop` and `hip-hop` tags include non-English music. Regional songs are filtered using genre tags, soundtrack-style titles ("From ...") and a manual artist blocklist (`BLOCK_ARTISTS` in `recommender.py`), so occasional misses remain.
- **Fixed catalog.** Songs missing from the dataset return "no match", and results can't include recent releases.
- **Noisy genre labels.** Some tracks carry unexpected genres, which changes what they're compared against.

## Ideas for next steps

- Re-rank candidates with listening-based similarity (for example Last.fm's `track.getSimilar`)
- Accept several seed songs and build a taste profile
- Add a language signal to replace the manual blocklist
- Tune feature weights against a larger set of rated examples

## Built with

Python · pandas · NumPy · RapidFuzz · Streamlit