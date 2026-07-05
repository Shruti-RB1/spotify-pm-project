import streamlit as st
from groq import Groq
import json
import random

st.set_page_config(page_title="Echo Decoder", page_icon="🎵", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #121212; color: white; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

REVIEWS = [
    {"id": 1, "src": "Spotify Community", "date": "Jun 2025", "rating": 1, "text": "Spotify has become utter trash recently. Recommendations always play the same songs. We're stuck in an echo chamber — I'm paying for Premium but I'll be quitting soon."},
    {"id": 2, "src": "Spotify Community", "date": "Jun 2025", "rating": 2, "text": "The algorithm has become nothing but an echo chamber. The radio just recommends what I was listening to before. Something changed and it's not good anymore."},
    {"id": 3, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "Discover Weekly keeps showing me songs I already know. That is not discovery — that is repetition with a new label on it. This used to be the best feature."},
    {"id": 4, "src": "App Store", "date": "Apr 2026", "rating": 3, "text": "Love Spotify overall but recommendations have become a closed loop. The more I listen, the narrower my suggestions get. No way to tell the app I want to explore."},
    {"id": 5, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "Removed Smart Shuffle and now discovery is terrible again. The AI recommendations just suggest songs I already saved. Paying premium for what exactly?"},
    {"id": 6, "src": "App Store", "date": "May 2026", "rating": 2, "text": "I wish Spotify had an exploration mode. Some days I want comfort, some days I want surprises. The app assumes I always want the same thing. No concept of intent."},
    {"id": 7, "src": "App Store", "date": "Feb 2026", "rating": 1, "text": "I hosted a party and played pop for 4 hours. Now all my recommendations are pop. It took 3 months to recover. Should separate party listening from personal taste."},
    {"id": 8, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Tried exploring jazz after years of indie rock. Radio kept pulling me back to indie. Zero cross-genre discovery support. The algorithm completely fails you if you want to branch out."},
    {"id": 9, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Music discovery is broken. After 2 years of Premium I've found maybe 5 new artists I genuinely like through recommendations. Always same genres, same sounds."},
    {"id": 10, "src": "Play Store", "date": "Apr 2026", "rating": 2, "text": "The AI recommendations feel optimized to keep me listening to familiar stuff, not to genuinely introduce me to new music. I want to grow my taste."},
    {"id": 11, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "When I first signed up, recommendations were interesting music I'd never heard before. Now I get the same songs and artists recommended over and over. How do I broaden this?"},
    {"id": 12, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "The algorithm has folded in on itself. It's created an echo chamber of an endlessly narrowing set of self-reinforcing sounds. Exposure to new tastes is wiped off the map."},
    {"id": 13, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "The recommendation engine is optimized for session length and completion rate. It gives me music I'll definitely finish, not music that might change my life."},
    {"id": 14, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "I use Spotify for work music AND music I love. The work playlist destroyed my recommendations. The algorithm doesn't know which me it's serving."},
    {"id": 15, "src": "Reddit", "date": "May 2026", "rating": None, "text": "I tried listening to new genres last month to shake up my recommendations. Zero difference. The algorithm ignores your intent. Trapped in a music bubble."},
    {"id": 16, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "No way to tell Spotify I'm in an exploring mood today. It assumes I always want comfort music. No concept of exploration intent vs comfort listening."},
    {"id": 17, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "4-year Premium subscriber. Every Discover Weekly, every Daily Mix — same 50 songs rotating. I rely on Reddit and YouTube for discovery now. Spotify is just playback."},
    {"id": 18, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "Please add an I'm feeling adventurous mode. Just a toggle. When on, show me things outside my usual genres. When off, familiar stuff. This cannot be that hard."},
    {"id": 19, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The problem is Spotify knows my taste too well. It has become a perfect mirror of who I was musically 2 years ago, not who I am or want to be now."},
    {"id": 20, "src": "App Store", "date": "Feb 2026", "rating": 2, "text": "Wish Spotify would show me why it recommended a song. Even one sentence. Recommendations are a black box I cannot trust. That is why I don't click on them."},
    {"id": 21, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "Been on Spotify Premium for 3 years. First year was amazing — discovering artists I never knew. Now Discover Weekly shows same 30 artists on rotation. Completely disappointed."},
    {"id": 22, "src": "App Store", "date": "Feb 2026", "rating": 1, "text": "My Discover Weekly is a joke. 70% of it are songs already in my library. The whole point is to discover NEW music. How is this still a problem after years?"},
    {"id": 23, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Spotify used to introduce me to underground artists. Now it's all mainstream stuff I've already heard everywhere. Miss the old discovery experience badly."},
    {"id": 24, "src": "Play Store", "date": "Apr 2026", "rating": 3, "text": "Daily Mix is great in theory but terrible in practice. It mixes my favourite songs with things I've heard hundreds of times. No actual new music ever shows up."},
    {"id": 25, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "Anyone else notice Spotify's algorithm gets worse the longer you use it? Year 1 was incredible for discovery. Year 3 and I'm hearing the same 200 songs forever."},
    {"id": 26, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "I've been liking songs across 5 new genres for 3 months hoping to teach Spotify I want variety. It learned nothing. Still serving the same indie rock I always listened to."},
    {"id": 27, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "The problem is there's no way to tell Spotify I'm curious about this genre, show me an entry point. It only knows what you've listened to, not what you're curious about."},
    {"id": 28, "src": "Spotify Community", "date": "Dec 2025", "rating": None, "text": "The algorithm learns from my passive background listening at work and ruins my personal recommendations. These should be completely separate profiles."},
    {"id": 29, "src": "App Store", "date": "Mar 2026", "rating": 1, "text": "Used Spotify for 5 years and discovery has gotten progressively worse each year. My Wrapped shows I discovered only 3 new artists this year. That is Spotify's fault."},
    {"id": 30, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "Radio stations are supposed to help you discover similar artists. Mine just plays the same artist I started with over and over again. That is not radio, that is a loop."},
    {"id": 31, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "I actively use Last.fm alongside Spotify because Spotify's discovery is so bad. Last.fm recommends genuinely obscure stuff based on my listening. Spotify just recommends Ed Sheeran."},
    {"id": 32, "src": "Reddit", "date": "May 2026", "rating": None, "text": "The issue is not that Spotify doesn't have enough music. It has everything. The curation layer completely fails to surface music I'd love but don't know about yet."},
    {"id": 33, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "I want to say I have been listening to dark folk lately, show me something adjacent but different. The app has no concept of adjacent but different."},
    {"id": 34, "src": "App Store", "date": "Apr 2026", "rating": 2, "text": "Used to use Spotify to discover music, now I use Reddit, YouTube and friends to discover and Spotify to play. Spotify has become a player app, not a discovery app."},
    {"id": 35, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Decent app overall but the discovery problem is real. After 18 months the algorithm feels like it has stopped learning. My tastes evolved but my recommendations have not."},
    {"id": 36, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "I subscribe to Spotify specifically for music discovery. But I am discovering more music through YouTube than Spotify. YouTube does not even have all the songs Spotify has."},
    {"id": 37, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "Does anyone actually use Discover Weekly anymore? Mine has been irrelevant for so long I forgot it existed. I check it occasionally and it is always disappointing."},
    {"id": 38, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "The algorithm treats every skip as rejection and every play-through as approval. But sometimes I let a song play because I am driving. That is not approval. The signal is noisy."},
    {"id": 39, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The algorithm optimises for what keeps me listening in the moment. It does not optimise for what would make me a more satisfied long-term subscriber. Short-term engagement vs long-term value."},
    {"id": 40, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "I have been on Spotify since 2015. Discovery was incredible then. Every Discover Weekly felt like a music lover made it for me personally. Now it is clearly just algorithmic garbage."},
    {"id": 41, "src": "Play Store", "date": "Mar 2026", "rating": 3, "text": "Love the app, hate the recommendation algorithm. It is like a friend who knew your music taste perfectly in 2020 but refuses to believe your taste has changed since then."},
    {"id": 42, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "Spotify has 100 million songs. I have heard maybe 500 of them regularly. The algorithm is doing essentially nothing to bridge that gap. Just recycling the 500 I already know."},
    {"id": 43, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "What I want: Here is a path from X to Y that will make sense to you with 5 stepping stone artists. What I get: Here is X again and also X-adjacent content you have heard before."},
    {"id": 44, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "I tried the AI DJ feature hoping it would help with discovery. It is just another playlist of familiar music with a voice between songs. More of the same with extra features."},
    {"id": 45, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "My listening context is different morning vs evening vs weekend. Spotify treats all my listening as one blob. A morning workout playlist is poisoning my evening chill recommendations."},
    {"id": 46, "src": "App Store", "date": "Apr 2026", "rating": 2, "text": "The algorithm learned I like lo-fi because I use it to study. Now every recommendation is ambient even though I only like it as background noise, not as music I actually enjoy."},
    {"id": 47, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Five years ago I discovered 50 plus artists through Spotify I still love. Last year I discovered maybe 3. Something has fundamentally changed in how the discovery engine works."},
    {"id": 48, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "Spotify says its algorithm analyses 100 plus signals. But none of those signals is what does this user want to discover today. That signal does not exist in the system at all."},
    {"id": 49, "src": "Reddit", "date": "May 2026", "rating": None, "text": "I genuinely believe the algorithm has gotten more conservative over time. Better to give you familiar music you won't skip than adventurous music you might hate."},
    {"id": 50, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "I know exactly what Spotify knows about me. What it does not know: my curiosity, my mood, my intention, my openness to something new. None of that is captured."},
]

SOURCES = ["All sources", "App Store", "Play Store", "Reddit", "Spotify Community"]

def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error(f"API key error: {e}")
        return None

def analyze_reviews(reviews_list):
    client = get_client()
    if not client:
        return None
    sample = random.sample(reviews_list, min(35, len(reviews_list)))
    block = "\n".join([f'[{i+1}] {r["src"]}: "{r["text"][:90]}"' for i, r in enumerate(sample)])
    prompt = f"""Analyze these {len(sample)} Spotify user reviews about music discovery. Return ONLY raw JSON, no markdown.

{block}

Return (max 3 items per array):
{{"headline":"insight under 15 words","discovery_pct":"X% cite discovery issues","sentiment":{{"negative":N,"neutral":N,"positive":N}},"barriers":[{{"title":"short","desc":"one sentence","severity":"Critical|High|Medium"}}],"frustrations":[{{"title":"short","desc":"one sentence","evidence":"5 words"}}],"behaviors":[{{"goal":"what users want","desc":"one sentence"}}],"repeat_causes":[{{"cause":"short","desc":"one sentence"}}],"segments":[{{"name":"name","size":"~X%","desc":"one sentence","pain":"one sentence"}}],"unmet_needs":[{{"need":"short","desc":"one sentence","priority":"Critical|High|Medium"}}],"root_cause":"two sentences","focus_segment":"one sentence"}}"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

# ── UI ──────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="background:rgba(29,185,84,0.15);border:1px solid #1DB954;border-radius:10px;padding:16px 20px;margin-bottom:20px;">
<p style="color:#1DB954;font-size:11px;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 6px;">
🎵 AI RESEARCH TOOL &nbsp;·&nbsp; App Store · Play Store · Reddit · Spotify Community
</p>
<h1 style="color:white;margin:0 0 6px;font-size:1.8rem;">Echo Decoder</h1>
<p style="color:#aaa;margin:0;font-size:14px;">AI-powered analysis of real Spotify user feedback — surfaces music discovery barriers at scale</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([2, 3])

with left:
    source = st.selectbox("Filter by source", SOURCES)
    shown = REVIEWS if source == "All sources" else [r for r in REVIEWS if r["src"] == source]
    st.markdown(f'<p style="color:#1DB954;font-weight:600;">📊 {len(REVIEWS)} reviews loaded · Showing {len(shown)}</p>', unsafe_allow_html=True)

    for r in shown[:30]:
        stars = ("★" * r["rating"] + "☆" * (5 - r["rating"])) if r["rating"] else "—"
        st.markdown(f"""<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;padding:10px;margin-bottom:8px;">
<div style="display:flex;justify-content:space-between;margin-bottom:5px;">
<span style="background:#2a2a2a;color:#aaa;padding:1px 8px;border-radius:10px;font-size:11px;">{r['src']}</span>
<span style="color:#f39c12;font-size:11px;">{stars} &nbsp; {r['date']}</span>
</div>
<p style="color:#ddd;font-size:12px;margin:0;line-height:1.6;">{r['text']}</p>
</div>""", unsafe_allow_html=True)

    if len(shown) > 30:
        st.caption(f"Showing 30 of {len(shown)} reviews")

    st.divider()
    if st.button(f"✨ Analyze {len(REVIEWS)} reviews with AI", type="primary", use_container_width=True):
        with st.spinner("Analyzing reviews with Llama 3.3... (~20 seconds)"):
            result = analyze_reviews(REVIEWS)
            if result:
                st.session_state["result"] = result
                st.rerun()

with right:
    if "result" not in st.session_state:
        st.markdown("""<div style="background:#1a1a1a;border:2px dashed #333;border-radius:12px;padding:3rem;text-align:center;margin-top:1rem;">
<p style="font-size:3rem;margin:0 0 12px;">📊</p>
<p style="color:#aaa;font-size:15px;font-weight:500;margin:0 0 6px;">Click Analyze to run AI analysis</p>
<p style="color:#555;font-size:13px;margin:0;">Answers 6 PM research questions<br>Powered by Groq · Llama 3.3 70B · Free</p>
</div>""", unsafe_allow_html=True)
    else:
        a = st.session_state["result"]

        st.markdown(f"""<div style="background:rgba(29,185,84,0.12);border:1px solid #1DB954;border-radius:8px;padding:14px 18px;margin-bottom:14px;">
<p style="color:#1DB954;font-size:10px;text-transform:uppercase;margin:0 0 5px;">KEY FINDING</p>
<p style="color:#1DB954;font-size:17px;font-weight:600;margin:0 0 6px;">{a.get("headline","")}</p>
<p style="color:#1DB954;font-size:12px;opacity:0.75;margin:0;">{a.get("discovery_pct","")}</p>
</div>""", unsafe_allow_html=True)

        s = a.get("sentiment", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("😤 Negative", f"{s.get('negative',0)}%")
        c2.metric("😐 Neutral", f"{s.get('neutral',0)}%")
        c3.metric("😊 Positive", f"{s.get('positive',0)}%")

        st.markdown("<br>", unsafe_allow_html=True)
        t1,t2,t3,t4,t5,t6 = st.tabs(["🚫 Barriers","👥 Segments","😤 Frustrations","💡 Needs","🎯 Behaviors","🔄 Repeat"])

        def color_badge(level):
            c = {"Critical":"#ff4444","High":"#ff8c00","Medium":"#1DB954"}.get(level,"#1DB954")
            return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{level}</span>'

        with t1:
            for b in a.get("barriers",[]):
                st.markdown(f"**{b['title']}** {color_badge(b['severity'])}", unsafe_allow_html=True)
                st.caption(b["desc"]); st.divider()
        with t2:
            for s in a.get("segments",[]):
                st.markdown(f"**{s['name']}** — *{s['size']}*")
                st.caption(s["desc"]); st.markdown(f"⚠️ {s['pain']}"); st.divider()
        with t3:
            for f in a.get("frustrations",[]):
                st.markdown(f"**{f['title']}**"); st.caption(f["desc"])
                if f.get("evidence"): st.markdown(f"> *{f['evidence']}*")
                st.divider()
        with t4:
            for n in a.get("unmet_needs",[]):
                st.markdown(f"**{n['need']}** {color_badge(n['priority'])}", unsafe_allow_html=True)
                st.caption(n["desc"]); st.divider()
        with t5:
            for b in a.get("behaviors",[]):
                st.markdown(f"**{b['goal']}**"); st.caption(b["desc"]); st.divider()
        with t6:
            for r in a.get("repeat_causes",[]):
                st.markdown(f"**{r['cause']}**"); st.caption(r["desc"]); st.divider()

        st.markdown(f"""<div style="background:rgba(255,180,0,0.1);border:1px solid #ffb800;border-radius:8px;padding:14px 18px;margin-top:10px;">
<p style="color:#ffb800;font-size:10px;text-transform:uppercase;margin:0 0 5px;">🔍 ROOT CAUSE</p>
<p style="color:#fff;font-size:13px;margin:0;line-height:1.75;">{a.get("root_cause","")}</p>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="background:#1a1a1a;border:1px solid #1DB954;border-radius:8px;padding:14px 18px;margin-top:10px;">
<p style="color:#1DB954;font-size:10px;text-transform:uppercase;margin:0 0 5px;">🎯 RECOMMENDED FOCUS SEGMENT</p>
<p style="color:#fff;font-size:13px;margin:0;line-height:1.75;">{a.get("focus_segment","")}</p>
</div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear results"):
            del st.session_state["result"]
            st.rerun()
