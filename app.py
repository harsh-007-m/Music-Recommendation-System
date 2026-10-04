import streamlit as st
from recommender import recommend

st.set_page_config(page_title="Music Recommender", page_icon="🎧", layout="centered")

st.title("🎧 Music Recommender")
st.caption("Type a song you like and get 5 others that sound similar.")

with st.form("search"):
    c1, c2 = st.columns(2)
    song = c1.text_input("Song title", placeholder="Blinding Lights")
    artist = c2.text_input("Artist (optional)", placeholder="The Weeknd")
    submitted = st.form_submit_button("Recommend", use_container_width=True)

if submitted and song:
    with st.spinner("Finding songs..."):
        matched, recs = recommend(song, artist or None)

    if matched is None:
        st.error("Song not found. Check the spelling or try adding the artist.")
    elif recs is None:
        st.warning("Found the song, but no similar tracks passed the filters.")
    else:
        st.subheader(f"Because you like “{matched['track_name']}” by {matched['artists']}")
        for _, r in recs.iterrows():
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**{r['track_name']}**  \n{r['artists']}")
                left.caption(f"Genre: {r['track_genre']}")
                right.markdown(f"[▶ Spotify](https://open.spotify.com/track/{r['track_id']})")
                st.progress(float(r["audio_sim"]), text=f"Sound match: {r['audio_sim']:.0%}")
elif submitted:
    st.info("Enter a song title first.")