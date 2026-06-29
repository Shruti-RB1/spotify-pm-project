import streamlit as st
from groq import Groq
import json

st.set_page_config(
    page_title="Echo Decoder — Spotify Discovery Intelligence",
    page_icon="🎵",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #121212; }
[data-testid="stHeader"] { background-color: #121212; }
.block-container { padding-top: 2rem; }
.stTabs [data-baseweb="tab"] { color: #999; }
.stTabs [aria-selected="true"] { color: #1DB954; }
div[data-testid="stMetricValue"] { color: #1DB954; font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

REVIEWS = [
    {"id": 1, "src": "Spotify Community", "date": "Jun 2025", "rating": 1, "text": "Spotify has become utter trash recently. Recommendations always play the same songs over and over again. We're stuck in an echo chamber — I'm paying for a subscription but I'll be quitting soon."},
    {"id": 2, "src": "Spotify Community", "date": "Jun 2025", "rating": 2, "text": "The algorithm has become nothing but an echo chamber. I'm seriously considering jumping ship. The radio just recommends what I was listening to before. Something changed and it's not good."},
    {"id": 3, "src": "Spotify Community", "date": "May 2025", "rating": 2, "text": "Premium user here. Spotify's algorithm used to be much better. I get tons of songs in styles of music I have never liked. If it doesn't change it's time to try others."},
    {"id": 4, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "When I first signed up, Spotify's recommendations were usually interesting music I'd never heard before. Now, I get the same songs and artists recommended to me over and over. How do I broaden what I get?"},
    {"id": 5, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "The algorithm has folded in on itself. It's created an echo chamber of an endlessly narrowing set of self-reinforcing sounds. Exposure to new tastes is wiped off the map."},
    {"id": 6, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "Discover Weekly keeps showing me songs I already know or have already liked. That is not discovery — that is repetition with a new label on it. This used to be the best feature. Now completely broken."},
    {"id": 7, "src": "App Store", "date": "Apr 2026", "rating": 3, "text": "Love Spotify overall but recommendations have become a closed loop. The more I listen, the narrower my suggestions get. I want to explore outside my usual genres but there's no way to tell the app that."},
    {"id": 8, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "Removed the Smart Shuffle feature and now discovery is terrible again. I'm back to manually digging through hundreds of playlists. The AI recommendations just suggest songs I've already saved."},
    {"id": 9, "src": "App Store", "date": "May 2026", "rating": 2, "text": "I wish Spotify had an exploration mode. Some days I want comfort listening, some days I want to be surprised. The app assumes I always want the same thing. No concept of listening intent at all."},
    {"id": 10, "src": "App Store", "date": "Feb 2026", "rating": 1, "text": "I hosted a party and played mainstream pop for 4 hours. Now all my recommendations are pop. It took 3 months for my algorithm to recover. Should separate party listening from my real personal taste."},
    {"id": 11, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Tried exploring jazz after years of indie rock. The Radio feature kept pulling me back to indie. Zero cross-genre discovery support. If you want to branch out, the algorithm completely fails you."},
    {"id": 12, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Music discovery is broken for me. After 2 years of Premium I've found maybe 5 new artists I genuinely like through recommendations. Always the same genres, same sounds, never pushes me toward something new."},
    {"id": 13, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "There's no way to tell Spotify I'm in an exploring mood today. It just assumes you always want comfort music. No concept of exploration intent vs comfort listening — two modes that simply don't exist in the product."},
    {"id": 14, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "4-year Premium subscriber. Every Discover Weekly, every Daily Mix, every Radio — same 50 songs rotating. I've started relying on Reddit and YouTube for actual discovery. Spotify is just a playback tool now."},
    {"id": 15, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "The recommendation engine is optimized for engagement — session length and completion rate. It gives me music I'll definitely finish, not music that might change my life. I want it to optimize for meaningful discovery."},
    {"id": 16, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "I use Spotify for focus/work music AND for music I actually love. The work playlist destroyed my recommendations. Everything I get now is sleep sounds. The algorithm doesn't know which me it's serving."},
    {"id": 17, "src": "Play Store", "date": "Apr 2026", "rating": 2, "text": "The AI recommendations feel optimized to keep me listening to familiar stuff, not to genuinely introduce me to new music. I want to grow my taste, not be fed the same playlist on repeat."},
    {"id": 18, "src": "Spotify Community", "date": "May 2026", "rating": None, "text": "Discover Weekly is suggesting genres I have never listened to and completely missing my actual taste. The algorithm is confused about who I am. It used to be spot-on."},
    {"id": 19, "src": "App Store", "date": "Feb 2026", "rating": 2, "text": "I tried to manually guide my algorithm by liking songs from new genres. Instead of adapting, it just mixed those genres randomly. There's no intelligent path for I want to expand in this direction."},
    {"id": 20, "src": "Reddit", "date": "May 2026", "rating": None, "text": "I specifically tried listening to new genres last month to shake up my recommendations. Zero difference. The algorithm ignores your intent. Feels like I am trapped in a music bubble with no escape hatch."},
]

SOURCES = ["All sources", "App Store", "Play Store", "Reddit", "Spotify Community"]

def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("⚠️ Add GROQ_API_KEY to Streamlit secrets.")
        return None

def analyze(reviews_list):
    client = get_client()
    if not client:
        return None
    block = "\n".join([
        f'[{i+1}] {r["src"]}: "{r["text"][:100]}"'
        for i, r in enumerate(reviews_list)
    ])
    prompt = f"""You are a senior product researcher at Spotify. Analyze these {len(reviews_list)} user reviews about music discovery. Return ONLY raw valid JSON — no markdown, no code fences, no explanation. Keep values concise.

REVIEWS:
{block}

Return this JSON (max 4 items per array):
{{
  "headline": "One insight under 15 words",
  "discovery_pct": "X% mention discovery issues",
  "sentiment": {{"negative": N, "neutral": N, "positive": N}},
  "barriers": [{{"title": "Short title", "desc": "One sentence", "severity": "Critical|High|Medium"}}],
  "frustrations": [{{"title": "Short title", "desc": "One sentence", "evidence": "5 words"}}],
  "behaviors": [{{"goal": "What users want", "desc": "One sentence"}}],
  "repeat_causes": [{{"cause": "Short title", "desc": "One sentence"}}],
  "segments": [{{"name": "Segment", "size": "~X%", "desc": "One sentence", "pain": "One sentence"}}],
  "unmet_needs": [{{"need": "Short title", "desc": "One sentence", "priority": "Critical|High|Medium"}}],
  "root_cause": "Two sentences max.",
  "focus_segment": "One sentence."
}}"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=3000,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error — please try again. ({e})")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

def badge(level):
    colors = {"Critical": "#ff4444", "High": "#ff8c00", "Medium": "#1DB954"}
    c = colors.get(level, "#1DB954")
    return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{level}</span>'

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown('<p style="color:#1DB954;font-size:12px;margin-bottom:4px;">AI RESEARCH TOOL · Real reviews · App Store, Play Store, Reddit, Community</p>', unsafe_allow_html=True)
st.markdown('<h1 style="color:white;margin-top:0;">🎵 Echo Decoder</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#999;margin-bottom:1.5rem;">AI-powered analysis of real Spotify user feedback — surfaces music discovery barriers at scale</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 3])

with col_left:
    src_filter = st.selectbox("Filter by source", SOURCES)
    filtered = REVIEWS if src_filter == "All sources" else [r for r in REVIEWS if r["src"] == src_filter]
    st.caption(f"Showing {len(filtered)} of {len(REVIEWS)} reviews")

    review_container = st.container(height=380)
    with review_container:
        for r in filtered:
            stars = ("★" * r["rating"] + "☆" * (5 - r["rating"])) if r["rating"] else ""
            st.markdown(f"""
<div style="background:#1e1e1e;border:1px solid #333;border-radius:8px;padding:10px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:4px;">
    <span style="background:#2a2a2a;color:#999;padding:1px 8px;border-radius:10px;font-size:11px;">{r['src']}</span>
    <span style="color:#f39c12;font-size:11px;">{stars}</span>
    <span style="color:#555;font-size:11px;">{r['date']}</span>
  </div>
  <p style="color:#ddd;font-size:12px;margin:0;line-height:1.6;">{r['text']}</p>
</div>""", unsafe_allow_html=True)

    st.divider()
    with st.expander("➕ Add a review"):
        new_src = st.selectbox("Source", ["App Store", "Play Store", "Reddit", "Spotify Community"])
        new_text = st.text_area("Review text", placeholder="Paste a user review here...", height=80)
        if st.button("Add review") and new_text.strip():
            REVIEWS.append({"id": len(REVIEWS)+1, "src": new_src, "date": "Jun 2026", "rating": 3, "text": new_text.strip()})
            st.success("Added!")
            st.rerun()

    st.divider()
    if st.button(f"✨ Analyze {len(REVIEWS)} reviews with AI", type="primary", use_container_width=True):
        with st.spinner("Running AI analysis... (~15 seconds)"):
            result = analyze(REVIEWS)
            if result:
                st.session_state["analysis"] = result
                st.rerun()

with col_right:
    if "analysis" not in st.session_state:
        st.markdown("""
<div style="background:#1e1e1e;border:2px dashed #333;border-radius:12px;padding:3rem;text-align:center;margin-top:1rem;">
  <p style="font-size:3rem;margin-bottom:12px;">📊</p>
  <p style="color:#aaa;font-size:15px;font-weight:500;margin-bottom:6px;">Click "Analyze reviews" to run AI analysis</p>
  <p style="color:#555;font-size:13px;">Answers 6 product discovery research questions<br>Powered by Groq · Llama 3.3 70B</p>
</div>""", unsafe_allow_html=True)
    else:
        a = st.session_state["analysis"]

        st.markdown(f"""
<div style="background:rgba(29,185,84,0.1);border:1px solid #1DB954;border-radius:8px;padding:12px 16px;margin-bottom:12px;">
  <p style="color:#1DB954;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 4px;">KEY FINDING</p>
  <p style="color:#1DB954;font-size:16px;font-weight:600;margin:0 0 6px;">{a.get('headline','')}</p>
  <p style="color:#1DB954;font-size:12px;opacity:0.8;margin:0;">{a.get('discovery_pct','')}</p>
</div>""", unsafe_allow_html=True)

        sent = a.get("sentiment", {})
        s1, s2, s3 = st.columns(3)
        s1.metric("Negative", f"{sent.get('negative', 0)}%")
        s2.metric("Neutral", f"{sent.get('neutral', 0)}%")
        s3.metric("Positive", f"{sent.get('positive', 0)}%")

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🚫 Barriers", "👥 Segments", "😤 Frustrations", "💡 Needs", "🎯 Behaviors", "🔄 Repeat"])

        with tab1:
            for b in a.get("barriers", []):
                st.markdown(f"**{b['title']}** {badge(b['severity'])}", unsafe_allow_html=True)
                st.caption(b['desc'])
                st.divider()

        with tab2:
            for s in a.get("segments", []):
                st.markdown(f"**{s['name']}** — *{s['size']}*")
                st.caption(s['desc'])
                st.markdown(f"⚠️ {s['pain']}")
                st.divider()

        with tab3:
            for f in a.get("frustrations", []):
                st.markdown(f"**{f['title']}**")
                st.caption(f['desc'])
                if f.get('evidence'):
                    st.markdown(f"> *{f['evidence']}*")
                st.divider()

        with tab4:
            for n in a.get("unmet_needs", []):
                st.markdown(f"**{n['need']}** {badge(n['priority'])}", unsafe_allow_html=True)
                st.caption(n['desc'])
                st.divider()

        with tab5:
            for beh in a.get("behaviors", []):
                st.markdown(f"**{beh['goal']}**")
                st.caption(beh['desc'])
                st.divider()

        with tab6:
            for rc in a.get("repeat_causes", []):
                st.markdown(f"**{rc['cause']}**")
                st.caption(rc['desc'])
                st.divider()

        st.markdown(f"""
<div style="background:rgba(255,180,0,0.1);border:1px solid #ffb800;border-radius:8px;padding:12px 16px;margin-top:8px;">
  <p style="color:#ffb800;font-size:10px;text-transform:uppercase;margin:0 0 4px;">ROOT CAUSE</p>
  <p style="color:#fff;font-size:13px;margin:0;line-height:1.7;">{a.get('root_cause','')}</p>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:#1e1e1e;border:1px solid #1DB954;border-radius:8px;padding:12px 16px;margin-top:8px;">
  <p style="color:#1DB954;font-size:10px;text-transform:uppercase;margin:0 0 4px;">RECOMMENDED FOCUS SEGMENT</p>
  <p style="color:#fff;font-size:13px;margin:0;line-height:1.7;">{a.get('focus_segment','')}</p>
</div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear results"):
            del st.session_state["analysis"]
            st.rerun()
