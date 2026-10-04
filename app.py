import hashlib
from html import escape

import streamlit as st

from recommender import recommend

st.set_page_config(page_title="Music Recommender", page_icon="🎧", layout="centered")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Figtree:wght@400;500;600&display=swap');

:root {
  --ink: #16182E;
  --muted: #5E627E;
  --surface: #FFFFFF;
  --line: #D9DCEE;
  --accent: #3A35E8;
}

html, body, .stApp, .stMarkdown, label, input, button {
  font-family: 'Figtree', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 760px; padding-top: 2.5rem; padding-bottom: 4rem; }

.hero {
  font-family: 'Bricolage Grotesque', 'Figtree', system-ui, sans-serif;
  font-weight: 700;
  font-size: clamp(2.1rem, 6vw, 3.2rem);
  line-height: 1.02;
  letter-spacing: -0.025em;
  margin: 0 0 0.6rem;
  color: var(--ink);
}
.sub { color: var(--muted); font-size: 1.05rem; line-height: 1.5; max-width: 46ch; margin: 0 0 1.75rem; }

[data-testid="stForm"] { border: none; padding: 0; }
[data-testid="stTextInput"] input { border-radius: 10px; border: 1px solid var(--line); }
[data-testid="stTextInput"] input:focus { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
[data-testid="stFormSubmitButton"] button { border-radius: 10px; font-weight: 600; min-height: 2.8rem; }

.hint { color: var(--muted); font-size: 0.9rem; margin: 1.25rem 0 0.4rem; }
.st-key-examples [data-testid="stVerticalBlock"] { flex-direction: row; flex-wrap: wrap; gap: 0.5rem; }
.st-key-examples [data-testid="stElementContainer"] { width: auto !important; flex: 0 0 auto; }
.st-key-examples button {
  border-radius: 999px; border: 1px solid var(--line); background: var(--surface);
  color: var(--ink); font-size: 0.88rem; min-height: 0; padding: 0.3rem 0.85rem;
}
.st-key-examples button:hover { border-color: var(--accent); color: var(--accent); }

.sleeve {
  flex: none;
  border-radius: 8px;
  background:
    radial-gradient(circle at 70% 70%, rgba(22, 24, 46, 0.92) 0 24%, transparent 25%),
    linear-gradient(135deg, var(--a), var(--b));
}

.seed { display: flex; gap: 14px; align-items: center; margin: 2rem 0 0.9rem; color: var(--muted); line-height: 1.35; }
.seed strong { color: var(--ink); }

.rec {
  display: flex; gap: 16px; align-items: center;
  background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
  padding: 14px 16px; margin-bottom: 10px;
}
.rec .meta { flex: 1; min-width: 0; }
.rec .t {
  font-family: 'Bricolage Grotesque', 'Figtree', system-ui, sans-serif;
  font-weight: 700; font-size: 1.12rem; color: var(--ink);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.rec .a { color: var(--muted); font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rec .foot { display: flex; align-items: center; gap: 12px; margin-top: 9px; }
.chip { font-size: 0.8rem; color: var(--ink); background: #E4E6F8; border-radius: 999px; padding: 2px 10px; white-space: nowrap; }
.bar { flex: 1; max-width: 160px; height: 4px; border-radius: 4px; background: var(--line); }
.bar > span { display: block; height: 100%; border-radius: 4px; background: var(--accent); }
.open {
  flex: none; font-size: 0.9rem; font-weight: 600; text-decoration: none;
  color: var(--accent) !important; border: 1px solid var(--accent); border-radius: 999px; padding: 6px 14px;
}
.open:hover { background: var(--accent); color: #fff !important; }
.open:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

@media (max-width: 560px) {
  .rec { flex-wrap: wrap; }
  .rec .meta { flex-basis: calc(100% - 80px); }
  .open { width: 100%; text-align: center; box-sizing: border-box; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

EXAMPLES = [
    ("Blinding Lights", "The Weeknd"),
    ("Mr. Brightside", "The Killers"),
    ("HUMBLE.", "Kendrick Lamar"),
    ("Heat Waves", "Glass Animals"),
    ("Someone Like You", "Adele"),
]


@st.cache_data(show_spinner=False)
def find(song, artist):
    return recommend(song, artist)


def hues(track_id):
    """Two stable hues per track, used to draw its generated cover."""
    h = int(hashlib.md5(str(track_id).encode()).hexdigest()[:8], 16)
    return h % 360, (h % 360 + 40 + (h >> 9) % 60) % 360


def sleeve(track_id, size):
    a, b = hues(track_id)
    return (f'<div class="sleeve" style="width:{size}px;height:{size}px;'
            f'--a:hsl({a} 72% 58%);--b:hsl({b} 68% 40%)"></div>')


def rec_row(r):
    pct = max(5, min(100, int(float(r["audio_sim"]) * 100)))
    tid = escape(str(r["track_id"]))
    return (
        '<div class="rec">'
        + sleeve(r["track_id"], 60)
        + '<div class="meta">'
        + f'<div class="t">{escape(str(r["track_name"]))}</div>'
        + f'<div class="a">{escape(str(r["artists"]).replace(";", ", "))}</div>'
        + '<div class="foot">'
        + f'<span class="chip">{escape(str(r["track_genre"]))}</span>'
        + f'<div class="bar" role="img" aria-label="Sound match"><span style="width:{pct}%"></span></div>'
        + '</div></div>'
        + f'<a class="open" href="https://open.spotify.com/track/{tid}" target="_blank" rel="noopener">Open in Spotify</a>'
        + '</div>'
    )


def use_example(song, artist):
    st.session_state.song_in = song
    st.session_state.artist_in = artist
    st.session_state.query = (song, artist)


# ---------- header ----------
st.markdown('<h1 class="hero">Find your next song</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub">Type a song you like and get five others that sound similar.</p>',
            unsafe_allow_html=True)

# ---------- search ----------
with st.form("search"):
    c1, c2 = st.columns(2)
    song = c1.text_input("Song title", key="song_in", placeholder="Blinding Lights")
    artist = c2.text_input("Artist (optional)", key="artist_in", placeholder="The Weeknd")
    submitted = st.form_submit_button("Find similar songs", type="primary", use_container_width=True)

if submitted:
    st.session_state.query = (song.strip(), artist.strip())

st.markdown('<div class="hint">Not sure where to start? Try one of these.</div>', unsafe_allow_html=True)
with st.container(key="examples"):
    for s, a in EXAMPLES:
        st.button(s, key=f"ex_{s}", on_click=use_example, args=(s, a))

# ---------- results ----------
query = st.session_state.get("query")
if query:
    q_song, q_artist = query
    if not q_song:
        st.info("Enter a song title to get started.")
    else:
        with st.spinner("Finding similar songs..."):
            matched, recs = find(q_song, q_artist or None)

        if matched is None:
            st.error(f"No match for “{q_song}”. Check the spelling, or add the artist to narrow it down.")
        elif recs is None:
            st.warning("Found the song, but no similar tracks passed the filters. Try a more popular song.")
        else:
            st.markdown(
                '<div class="seed">'
                + sleeve(matched["track_id"], 44)
                + f'<div>Because you like <strong>{escape(str(matched["track_name"]))}</strong>'
                + f' by {escape(str(matched["artists"]).replace(";", ", "))}</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("".join(rec_row(r) for _, r in recs.iterrows()), unsafe_allow_html=True)

with st.expander("How recommendations are chosen"):
    st.write(
        "Songs are compared by how they sound: tempo, energy, mood, acousticness and more. "
        "Candidates come from the same genre and are popular enough to be familiar, and each artist "
        "appears once. Lyrics, language and listening history aren't used, so some picks will miss."
    )