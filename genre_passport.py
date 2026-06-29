import streamlit as st
from groq import Groq
import json

st.set_page_config(
    page_title="Genre Passport — AI Music Discovery",
    page_icon="✈️",
    layout="centered"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #121212; }
[data-testid="stHeader"] { background-color: #121212; }
.block-container { padding-top: 2rem; max-width: 680px; }
</style>
""", unsafe_allow_html=True)

ADVENTURE_LABELS = {1: "Gentle nudge", 2: "A new lane", 3: "Branching out", 4: "New territory", 5: "Full passport"}
FAM_LABELS = ["comfort zone", "familiar", "adjacent", "new territory", "uncharted"]

def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("⚠️ Add GROQ_API_KEY to Streamlit secrets.")
        return None

def generate_journey(taste_input, adventure):
    client = get_client()
    if not client:
        return None
    prompt = f"""You are Genre Passport, an AI music discovery feature on Spotify. Create a 5-song discovery journey that logically bridges from the user's familiar taste to something genuinely new.

User's taste: "{taste_input}"
Adventure level: {adventure}/5 (1=slight nudge, 5=radical genre departure)

Rules:
- Song 1 must feel very familiar (familiarity: 1-2)
- Each song moves progressively further from comfort zone
- Song 5 reaches the adventure level destination
- Use real songs by real artists that actually exist
- Keep all text under 20 words per field
- bridge_note should be empty string "" for the last song

Return ONLY raw valid JSON (no markdown, no explanation):
{{
  "journey_title": "4-6 word title",
  "tagline": "One sentence",
  "departure": "One sentence",
  "destination": "One sentence",
  "songs": [
    {{
      "position": 1,
      "artist": "Artist Name",
      "title": "Song Title",
      "year": 2020,
      "familiarity": 1,
      "genre_tags": ["tag1", "tag2"],
      "why_you": "One sentence why this fits their taste",
      "whats_new": "One sentence what new element this introduces",
      "bridge_note": "One sentence how this leads to next song"
    }}
  ],
  "insight": "One sentence about the user's musical potential"
}}"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.error(f"Could not generate journey — please try again.")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Session state
for key, val in [("page", "onboard"), ("journey", None), ("adventure", 3), ("taste", ""), ("feedback", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── ONBOARD ────────────────────────────────────────────────────────────────────
if st.session_state.page == "onboard":
    st.markdown("""
<div style="text-align:center;padding:1rem 0 1.5rem;">
  <p style="color:#1DB954;font-size:11px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">AI-NATIVE FEATURE · Spotify Growth Team</p>
  <h1 style="color:white;font-size:2.5rem;margin:0 0 12px;">✈️ Genre Passport</h1>
  <p style="color:#999;font-size:15px;line-height:1.7;max-width:480px;margin:0 auto;">
    Break out of your listening bubble. Describe your taste and we'll build a 5-song journey from your comfort zone to somewhere you've never been — with bridges that actually make sense.
  </p>
</div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "💬", "Intent-aware", "Understands what you want, not just what you played"),
        (c2, "🛤️", "Bridged paths", "Logical musical bridges, never random genre jumps"),
        (c3, "👁️", "Transparent", "Explains exactly why each song was chosen"),
    ]:
        with col:
            st.markdown(f"""
<div style="background:#1e1e1e;border:1px solid #333;border-radius:10px;padding:14px;text-align:center;height:130px;">
  <p style="font-size:22px;margin:0 0 6px;">{icon}</p>
  <p style="color:white;font-weight:600;font-size:12px;margin:0 0 4px;">{title}</p>
  <p style="color:#777;font-size:11px;margin:0;">{desc}</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style="background:#1e1e1e;border:1px solid #333;border-radius:10px;padding:14px;margin-bottom:1.5rem;">
  <p style="color:#999;font-size:12px;font-weight:600;margin:0 0 10px;">Why Discover Weekly isn't enough</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    <div style="background:#1a1010;border:1px solid #3a2020;border-radius:6px;padding:10px;">
      <p style="color:#ff6b6b;font-size:11px;font-weight:600;margin:0 0 6px;">Discover Weekly</p>
      <p style="color:#888;font-size:11px;line-height:1.6;margin:0;">Based on what you already heard<br>No way to signal "I want something new"<br>No explanation for any recommendation</p>
    </div>
    <div style="background:#101a10;border:1px solid #203a20;border-radius:6px;padding:10px;">
      <p style="color:#1DB954;font-size:11px;font-weight:600;margin:0 0 6px;">Genre Passport</p>
      <p style="color:#888;font-size:11px;line-height:1.6;margin:0;">Based on what you tell it you want<br>You control how far to go<br>Explains every recommendation</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    if st.button("✈️ Start your discovery journey", type="primary", use_container_width=True):
        st.session_state.page = "input"
        st.rerun()

# ── INPUT ──────────────────────────────────────────────────────────────────────
elif st.session_state.page == "input":
    if st.button("← Back to home"):
        st.session_state.page = "onboard"
        st.rerun()

    st.markdown('<h2 style="color:white;">Tell us about your taste</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#999;margin-bottom:1rem;">The more specific, the better your journey. Describe artists, songs, moods, or what you\'re looking for.</p>', unsafe_allow_html=True)

    taste = st.text_area(
        "What are you listening to lately?",
        value=st.session_state.taste,
        placeholder="e.g. I love Arijit Singh and emotional Bollywood — slow, melancholy songs. But lately it all sounds the same and I want something with more energy and rhythm.",
        height=110
    )

    adv = st.slider("How adventurous do you want to go?", 1, 5, st.session_state.adventure)
    st.caption(f"**{ADVENTURE_LABELS[adv]}** — {'Stay close to what you know' if adv <= 2 else 'Explore new musical territory' if adv <= 3 else 'Go somewhere completely new'}")

    st.session_state.adventure = adv
    st.session_state.taste = taste

    if st.button("✨ Generate my discovery journey", type="primary", use_container_width=True, disabled=not taste.strip()):
        with st.spinner("Building your journey... (~15 seconds)"):
            journey = generate_journey(taste, adv)
            if journey:
                st.session_state.journey = journey
                st.session_state.feedback = None
                st.session_state.page = "journey"
                st.rerun()

# ── JOURNEY ────────────────────────────────────────────────────────────────────
elif st.session_state.page == "journey" and st.session_state.journey:
    j = st.session_state.journey

    if st.button("← New journey"):
        st.session_state.page = "input"
        st.session_state.journey = None
        st.rerun()

    st.markdown(f"""
<div style="margin-bottom:1rem;">
  <p style="color:#1DB954;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 4px;">YOUR DISCOVERY JOURNEY · Adventure {st.session_state.adventure}/5</p>
  <h2 style="color:white;font-size:1.6rem;margin:0 0 4px;">{j.get('journey_title', 'Your Journey')}</h2>
  <p style="color:#999;font-size:14px;margin:0;">{j.get('tagline', '')}</p>
</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
<div style="background:rgba(29,185,84,0.1);border:1px solid #1DB954;border-radius:8px;padding:10px 12px;">
  <p style="color:#1DB954;font-size:9px;text-transform:uppercase;margin:0 0 3px;">Departing from</p>
  <p style="color:white;font-size:12px;margin:0;">{j.get('departure', '')}</p>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div style="background:rgba(255,180,0,0.1);border:1px solid #ffb800;border-radius:8px;padding:10px 12px;">
  <p style="color:#ffb800;font-size:9px;text-transform:uppercase;margin:0 0 3px;">Arriving at</p>
  <p style="color:white;font-size:12px;margin:0;">{j.get('destination', '')}</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    bar_colors = ["#1DB954", "#1DB954", "#ffb800", "#ff8c00", "#ff4444"]

    for song in j.get("songs", []):
        pos = song.get("position", 1)
        color = bar_colors[min(pos - 1, 4)]
        fam = song.get("familiarity", 3)
        fam_dots = "●" * fam + "○" * (5 - fam)
        tags = " · ".join(song.get("genre_tags", []))

        with st.expander(f"**{pos}. {song.get('artist', '')} — {song.get('title', '')}** ({song.get('year', '')})", expanded=(pos == 1)):
            st.markdown(f'<p style="color:{color};font-size:12px;margin-bottom:4px;">{fam_dots} {FAM_LABELS[min(fam-1, 4)]}</p>', unsafe_allow_html=True)
            if tags:
                st.caption(tags)
            st.markdown("<br>", unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown(f'<p style="color:#1DB954;font-size:10px;font-weight:600;text-transform:uppercase;margin:0 0 4px;">Why this connects to you</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="color:#ddd;font-size:13px;margin:0;">{song.get("why_you", "")}</p>', unsafe_allow_html=True)
            with cc2:
                st.markdown(f'<p style="color:#ffb800;font-size:10px;font-weight:600;text-transform:uppercase;margin:0 0 4px;">What\'s new here</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="color:#ddd;font-size:13px;margin:0;">{song.get("whats_new", "")}</p>', unsafe_allow_html=True)
            if song.get("bridge_note"):
                st.markdown(f'<p style="color:#555;font-size:11px;font-style:italic;margin-top:10px;padding-top:8px;border-top:1px solid #333;">→ {song.get("bridge_note", "")}</p>', unsafe_allow_html=True)

    if j.get("insight"):
        st.markdown(f"""
<div style="background:rgba(255,180,0,0.1);border:1px solid #ffb800;border-radius:8px;padding:12px 16px;margin-top:16px;">
  <p style="color:#ffb800;font-size:10px;text-transform:uppercase;margin:0 0 4px;">💡 DISCOVERY INSIGHT</p>
  <p style="color:white;font-size:13px;margin:0;line-height:1.7;">{j.get('insight', '')}</p>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.feedback:
        st.markdown('<p style="color:#999;font-size:13px;font-weight:500;">Was this journey useful?</p>', unsafe_allow_html=True)
        fb1, fb2, fb3 = st.columns(3)
        with fb1:
            if st.button("👍 Yes, helpful", use_container_width=True):
                st.session_state.feedback = "helpful"
                st.rerun()
        with fb2:
            if st.button("🚀 Too familiar", use_container_width=True):
                st.session_state.feedback = "too_familiar"
                st.rerun()
        with fb3:
            if st.button("😅 Too adventurous", use_container_width=True):
                st.session_state.feedback = "too_adventurous"
                st.rerun()
    else:
        msgs = {"helpful": "✅ Great! Your passport improves with each journey.", "too_familiar": "Got it — try increasing the adventure level next time.", "too_adventurous": "Got it — try a lower adventure level next time."}
        st.success(msgs.get(st.session_state.feedback, "Thanks for the feedback!"))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✈️ Plan a new journey", type="primary", use_container_width=True):
        st.session_state.page = "input"
        st.session_state.journey = None
        st.session_state.feedback = None
        st.rerun()
