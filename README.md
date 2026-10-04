# 🎧 Music Recommender
 
Type in a song you like and get 5 others that sound similar. Built with Python, pandas, NumPy and Streamlit, using Spotify audio features.
 
**Live demo:** 
 
## How it works
 
1. **Find the song.** Fuzzy title matching (RapidFuzz), with an optional artist filter. If several songs share a title, the most popular one is used.
2. **Pick candidates.** Only songs that share a genre with the input song and have a popularity score of at least 50.
3. **Rank by sound.** Each candidate is scored by its Euclidean distance to the input song across 12 audio features, plus a small popularity bonus.
4. **Clean up the list.** One result per artist, alternate versions of the same song collapsed, and regional or non-English tracks removed unless the input song is itself regional.
### Audio features used
 
`danceability`, `energy`, `acousticness`, `instrumentalness`, `liveness`, `speechiness`, `valence`, `tempo`, `loudness`, `key` (encoded as `key_sin` / `key_cos` because it is circular), and `mode`.
 
Features are transformed and weighted before comparison: `speechiness` and `liveness` are log-transformed, tiny `instrumentalness` values are zeroed, `loudness` is clipped at -25 dB, and everything is standardized. Features describing the overall feel of a song (energy, danceability, acousticness, valence, instrumentalness) get the highest weights. `key` and `mode` get the lowest.
 
## Project structure
 
```
music/
├── app.py                 # Streamlit interface
├── recommender.py         # search + recommendation logic
├── requirements.txt
├── data/
│   ├── spotify_tracks_final.csv   # cleaned catalog (~79k tracks)
│   └── X_scaled.npy               # processed feature matrix
└── notebooks/
    ├── 01_data_preprocessing.ipynb
    └── 02_feature_engineering.ipynb
```
 
## Data preparation
 
Starting from a Spotify tracks dataset (Kaggle) of about 113k rows, the pipeline:
 
- removes missing values and exact duplicates
- merges repeated copies of the same track (it appears once per genre) into one row, keeping all genres in `all_genres`
- collapses re-releases that share a cleaned title and artist
- drops broken tracks (tempo or time signature of 0, durations under 30 seconds or over 15 minutes, near-silent loudness)
- drops spoken-word content (speechiness above 0.8) and comedy
This leaves about 79,000 tracks.
 
## Run it locally
 
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
pip install -r requirements.txt
streamlit run app.py
```
 
## Deploy
 
The app runs on [Streamlit Community Cloud](https://share.streamlit.io): connect the GitHub repo, set the main file to `app.py`, and deploy.
 
## Limitations
 
- **Audio features describe sound, not taste.** They don't capture era, lyrics, language or which songs listeners actually play together, so some matches are "similar sounding" without being "something you'd put on one playlist".
- **No language column.** The dataset's `pop` and `hip-hop` tags include non-English music, so regional filtering relies on genre tags, soundtrack-style titles and a manual artist blocklist (`BLOCK_ARTISTS` in `recommender.py`). Occasional leaks are possible.
- **Limited catalog.** Songs missing from the dataset return "Song not found".
- **Genre tags are noisy.** Some songs carry unexpected genre labels, which affects their results.
## Ideas for improvement
 
- Re-rank candidates using listening-based similarity (for example Last.fm's `track.getSimilar`)
- Support multiple seed songs to build a taste profile
- Add a language or region signal to remove the need for the blocklist
- Tune feature weights with a larger listening test
## Tech stack
 
Python · pandas · NumPy · RapidFuzz · Streamlit
 