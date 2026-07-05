import streamlit as st
from groq import Groq
import json
import random

st.set_page_config(
    page_title="Echo Decoder — Spotify Discovery Intelligence",
    page_icon="🎵",
    layout="wide"
)

st.markdown("""
<style>
/* Force dark background everywhere */
html, body { background-color: #121212 !important; }
[data-testid="stApp"] { background-color: #121212 !important; }
[data-testid="stAppViewContainer"] { background-color: #121212 !important; }
[data-testid="stHeader"] { background-color: #121212 !important; }
[data-testid="stSidebar"] { background-color: #1a1a1a !important; }
[data-testid="stMainBlockContainer"] { background-color: #121212 !important; }
.block-container { padding-top: 1.5rem; background-color: #121212; }
/* Text colors */
h1, h2, h3, p, label, .stMarkdown { color: #FFFFFF !important; }
.stSelectbox label, .stTextArea label, .stSlider label { color: #FFFFFF !important; }
/* Tabs */
.stTabs [data-baseweb="tab-list"] { background-color: #1e1e1e; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { color: #999 !important; }
.stTabs [aria-selected="true"] { color: #1DB954 !important; }
/* Metrics */
div[data-testid="stMetricValue"] { color: #1DB954 !important; }
/* Buttons */
.stButton button[kind="primary"] { background-color: #1DB954; border: none; color: white; }
.stButton button[kind="primary"]:hover { background-color: #17a349; }
/* Expander */
.streamlit-expanderHeader { color: #FFFFFF !important; background-color: #1e1e1e !important; }
/* Input fields */
.stTextArea textarea { background-color: #1e1e1e !important; color: #fff !important; border-color: #333 !important; }
.stSelectbox div[data-baseweb="select"] { background-color: #1e1e1e !important; }
</style>
""", unsafe_allow_html=True)

ALL_REVIEWS = [
    {"id": 1, "src": "Spotify Community", "date": "Jun 2025", "rating": 1, "text": "Spotify has become utter trash recently. Recommendations always play the same songs over and over again. We're stuck in an echo chamber — I'm paying for a subscription but I'll be quitting soon."},
    {"id": 2, "src": "Spotify Community", "date": "Jun 2025", "rating": 2, "text": "The algorithm has become nothing but an echo chamber. I'm seriously considering jumping ship. The radio just recommends what I was listening to before. Something changed and it's not good anymore."},
    {"id": 3, "src": "Spotify Community", "date": "May 2025", "rating": 2, "text": "Premium user here. Spotify's algorithm used to be much better. I get tons of songs in styles of music I have never liked. If it doesn't change it's time to try others."},
    {"id": 4, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "When I first signed up, Spotify's recommendations were usually interesting music I'd never heard before. Now, I get the same songs and artists recommended to me over and over. How do I broaden what I get?"},
    {"id": 5, "src": "Reddit", "date": "Sep 2025", "rating": None, "text": "The algorithm has folded in on itself. It's created an echo chamber of an endlessly narrowing set of self-reinforcing sounds. Exposure to new tastes is wiped off the map entirely."},
    {"id": 6, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "Discover Weekly keeps showing me songs I already know. That is not discovery — that is repetition with a new label on it. This used to be the best feature. Now completely broken for me."},
    {"id": 7, "src": "App Store", "date": "Apr 2026", "rating": 3, "text": "Love Spotify overall but recommendations have become a closed loop. The more I listen, the narrower my suggestions get. I want to explore outside my usual genres but there's no way to tell the app that."},
    {"id": 8, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "Removed the Smart Shuffle feature and now discovery is terrible again. I'm back to manually digging through hundreds of playlists. The AI recommendations just suggest songs I've already saved."},
    {"id": 9, "src": "App Store", "date": "May 2026", "rating": 2, "text": "I wish Spotify had an exploration mode. Some days I want comfort listening, some days I want to be surprised. The app assumes I always want the same thing. No concept of listening intent at all."},
    {"id": 10, "src": "App Store", "date": "Feb 2026", "rating": 1, "text": "I hosted a party and played mainstream pop for 4 hours. Now all my recommendations are pop. It took 3 months for my algorithm to recover. Should separate party listening from my real personal taste."},
    {"id": 11, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Tried exploring jazz after years of indie rock. The Radio feature kept pulling me back to indie. Zero cross-genre discovery support. If you want to branch out, the algorithm completely fails you."},
    {"id": 12, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Music discovery is broken for me. After 2 years of Premium I've found maybe 5 new artists I genuinely like through recommendations. Always the same genres, same sounds."},
    {"id": 13, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "There's no way to tell Spotify I'm in an exploring mood today. It just assumes you always want comfort music. No concept of exploration intent vs comfort listening in the product."},
    {"id": 14, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "4-year Premium subscriber. Every Discover Weekly, every Daily Mix — same 50 songs rotating. I've started relying on Reddit and YouTube for actual discovery. Spotify is just a playback tool."},
    {"id": 15, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "The recommendation engine is optimized for engagement — session length and completion rate. It gives me music I'll definitely finish, not music that might change my life."},
    {"id": 16, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "I use Spotify for focus/work music AND for music I actually love. The work playlist destroyed my recommendations. The algorithm doesn't know which me it's serving."},
    {"id": 17, "src": "Play Store", "date": "Apr 2026", "rating": 2, "text": "The AI recommendations feel optimized to keep me listening to familiar stuff, not to genuinely introduce me to new music. I want to grow my taste, not hear the same playlist on repeat."},
    {"id": 18, "src": "Spotify Community", "date": "May 2026", "rating": None, "text": "Discover Weekly is suggesting genres I have never listened to and completely missing my actual taste. The algorithm is confused about who I am. It used to be spot-on."},
    {"id": 19, "src": "App Store", "date": "Feb 2026", "rating": 2, "text": "I tried to manually guide my algorithm by liking songs from new genres. Instead of adapting, it just mixed those genres randomly. There's no intelligent path for 'I want to expand in this direction'."},
    {"id": 20, "src": "Reddit", "date": "May 2026", "rating": None, "text": "I specifically tried listening to new genres last month to shake up my recommendations. Zero difference. The algorithm ignores your intent. Trapped in a music bubble with no escape hatch."},
    {"id": 21, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "Been on Spotify Premium for 3 years. The first year was amazing — discovering artists I never knew existed. Now Discover Weekly shows me the same 30 artists on rotation. Completely disappointed."},
    {"id": 22, "src": "App Store", "date": "Feb 2026", "rating": 1, "text": "My Discover Weekly playlist is a joke. 70% of it are songs already in my library. The whole point is to discover NEW music. How is this still a problem after years of development?"},
    {"id": 23, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Spotify used to introduce me to underground artists I'd never find otherwise. Now it's all mainstream stuff I've already heard everywhere. Miss the old discovery experience badly."},
    {"id": 24, "src": "Play Store", "date": "Apr 2026", "rating": 3, "text": "The Daily Mix feature is great in theory but terrible in practice. It mixes my favourite songs with things I've already heard hundreds of times. No actual new music ever shows up."},
    {"id": 25, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "Anyone else notice that Spotify's algorithm gets worse the longer you use it? Year 1 was incredible for discovery. Year 3 and I'm basically hearing the same 200 songs forever."},
    {"id": 26, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "I've been systematically liking songs across 5 new genres over 3 months hoping to teach Spotify I want variety. It learned nothing. Still serving me the same indie rock I've always listened to."},
    {"id": 27, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "The problem is there's no way to tell Spotify 'I'm curious about this genre, show me an entry point'. It only knows what you've listened to, not what you're curious about."},
    {"id": 28, "src": "Spotify Community", "date": "Dec 2025", "rating": None, "text": "I've reported this so many times. The algorithm learns from my passive background listening at work and ruins my personal playlist recommendations. These should be completely separate."},
    {"id": 29, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "My partner and I share a family account and now the algorithm is completely broken for both of us because it can't distinguish between our completely different music tastes."},
    {"id": 30, "src": "App Store", "date": "Mar 2026", "rating": 1, "text": "I've been using Spotify for 5 years and the discovery has gotten progressively worse each year. My Wrapped shows I discovered only 3 new artists this year. That's not Spotify's fault... actually it is."},
    {"id": 31, "src": "Play Store", "date": "Jan 2026", "rating": 2, "text": "The Blend feature with friends is fun but doesn't help discovery. I want something that takes me outside my friend group's tastes, not just combines them into a mediocre mix."},
    {"id": 32, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "Radio stations on Spotify are supposed to help you discover similar artists. Mine just plays the same artist I started with over and over again. That's not radio, that's a loop."},
    {"id": 33, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "I actively use Last.fm alongside Spotify because Spotify's discovery is so bad now. Last.fm recommends genuinely obscure stuff based on my listening. Spotify just recommends Ed Sheeran."},
    {"id": 34, "src": "Reddit", "date": "May 2026", "rating": None, "text": "The issue isn't that Spotify doesn't have enough music. It has everything. The issue is the curation layer completely fails to surface music I'd love but don't know about yet."},
    {"id": 35, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "I want to be able to say 'I've been listening to a lot of dark folk lately, show me something adjacent but different.' The app has no concept of 'adjacent but different'."},
    {"id": 36, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "Spotify knows I like sad music. It doesn't know I want to be challenged by new sad music, not comforted by familiar sad music. Big difference. No feature addresses this."},
    {"id": 37, "src": "App Store", "date": "Apr 2026", "rating": 2, "text": "Used to use Spotify to discover music, now I use Reddit, YouTube and friend recommendations to discover and Spotify to play. Spotify has become a player app, not a discovery app."},
    {"id": 38, "src": "App Store", "date": "May 2026", "rating": 1, "text": "The more I use Spotify, the worse it gets at finding me new music. This is the opposite of how it should work. More data should mean better recommendations, not worse."},
    {"id": 39, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Decent app overall but the discovery problem is real. After 18 months the algorithm feels like it's stopped learning. My tastes have evolved but my recommendations haven't."},
    {"id": 40, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "Three suggestions for Spotify: 1. Let me say when I want discovery vs comfort mode. 2. Explain why songs are recommended. 3. Let me block certain artists from appearing. None of these exist."},
    {"id": 41, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "I subscribe to Spotify specifically for music discovery. But I'm discovering more music through YouTube recommendations than through Spotify. YouTube doesn't even have all the songs Spotify has."},
    {"id": 42, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "Honest question: does anyone actually use Discover Weekly anymore? Mine has been irrelevant for so long I forgot it existed. I check it occasionally and it's always disappointing."},
    {"id": 43, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "The algorithm treats every skip as rejection and every play-through as approval. But sometimes I let a song play because I'm driving. That's not approval. The signal is completely noisy."},
    {"id": 44, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "Feature request: let me rate songs not just with heart/skip but with mood tags. 'Great but not now' or 'Want to explore more like this'. Binary feedback creates a binary algorithm."},
    {"id": 45, "src": "Spotify Community", "date": "May 2026", "rating": None, "text": "The algorithm optimises for what keeps me listening in the moment. It doesn't optimise for what would make me a more satisfied long-term subscriber. Short-term engagement vs long-term value."},
    {"id": 46, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "I've been on Spotify since 2015. Discovery was incredible then. Every Discover Weekly felt like a music lover made it for me personally. Now it's clearly just algorithmic garbage."},
    {"id": 47, "src": "App Store", "date": "Feb 2026", "rating": 2, "text": "Tried switching to Apple Music for discovery, then back to Spotify for the library. Both have the same problem. But Spotify's was supposed to be the best. It isn't anymore."},
    {"id": 48, "src": "Play Store", "date": "Mar 2026", "rating": 3, "text": "Love the app, hate the recommendation algorithm. It's like a friend who knew your music taste perfectly in 2020 but refuses to believe your taste has changed at all since then."},
    {"id": 49, "src": "Play Store", "date": "Apr 2026", "rating": 1, "text": "Genuinely baffled at how Spotify with all its data and engineering can have worse music discovery than a random music blog from 2008. The curation quality has collapsed completely."},
    {"id": 50, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "Spotify has 100 million songs. I've heard maybe 500 of them regularly. The algorithm is doing essentially nothing to bridge that gap. It's just recycling the 500 I already know."},
    {"id": 51, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "What I want: 'You like X. Here's a path from X to Y that will make sense to you, with 5 stepping stone artists.' What I get: 'Here's X again, and also X-adjacent content you've heard before.'"},
    {"id": 52, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "The algorithm won't recommend anything with fewer than 100k monthly listeners. So independent artists are invisible to me unless I specifically search for them. Discovery is dead for emerging artists."},
    {"id": 53, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "I tried the AI DJ feature hoping it would help with discovery. It's just another playlist of familiar music with a voice between songs. More of the same with extra features, not actually new."},
    {"id": 54, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "Release Radar is the only discovery feature that still works for me, because it forces new content (new releases by artists I like). Every other feature just loops familiar stuff."},
    {"id": 55, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "My listening context is completely different in the morning vs evening vs weekend. Spotify treats all my listening as one blob. A morning workout playlist is poisoning my evening chill recommendations."},
    {"id": 56, "src": "App Store", "date": "Apr 2026", "rating": 2, "text": "The algorithm learned I like lo-fi because I use it to study. Now every recommendation is ambient/lo-fi even though I only like it as background noise, not as music I actually enjoy."},
    {"id": 57, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Five years ago I discovered 50+ artists through Spotify I still love. Last year I discovered maybe 3. Something has fundamentally changed in how the discovery engine works."},
    {"id": 58, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "The recommendation algorithm seems to be optimised to minimise the chance of you skipping. So it plays safe. But 'songs I won't skip' and 'songs that change my life' are completely different lists."},
    {"id": 59, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "Spotify says its algorithm analyses 100+ signals. But none of those signals is 'what does this user want to discover today'. That signal doesn't exist in the system at all."},
    {"id": 60, "src": "Reddit", "date": "May 2026", "rating": None, "text": "I genuinely believe the algorithm has gotten more conservative over time because Spotify is scared of churn. Better to give you familiar music you won't skip than adventurous music you might hate."},
    {"id": 61, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "Please add an 'I'm feeling adventurous' mode. Just a toggle. When on, show me things outside my usual genres. When off, show me familiar stuff. This can't be that hard to build."},
    {"id": 62, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The problem isn't that Spotify doesn't know my taste. It knows it too well. It's become a perfect mirror of who I was musically 2 years ago, not who I am or want to be now."},
    {"id": 63, "src": "App Store", "date": "May 2026", "rating": 2, "text": "Wish Spotify would show me why it recommended a song. Even one sentence. 'Because you liked X' at least gives me information. Right now recommendations are a black box I can't trust."},
    {"id": 64, "src": "App Store", "date": "Jan 2026", "rating": 1, "text": "Rating Spotify 1 star specifically for music discovery. Everything else is fine. But discovery, which should be a flagship feature, is broken. My recommendations haven't improved in 18 months."},
    {"id": 65, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "I want Spotify to be able to tell me: here's a genre you've never listened to, here's why someone with your taste might love it, here are 5 entry points. It cannot do any of this."},
    {"id": 66, "src": "Play Store", "date": "Mar 2026", "rating": 3, "text": "The discovery problem is so bad I've started scheduling time every week to manually browse genres and artist pages just to find new music. That shouldn't be necessary on a platform with 100M songs."},
    {"id": 67, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "My music taste has changed dramatically in the past 2 years. Spotify has no idea. Its model of me is completely outdated. And there's no mechanism to say 'start fresh, relearn who I am'."},
    {"id": 68, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "Tried the trick of creating a fresh Spotify account to get better discovery. Worked great for 6 months. Then the algorithm calcified again. The problem is structural, not solvable by starting over."},
    {"id": 69, "src": "Reddit", "date": "Mar 2026", "rating": None, "text": "What Spotify calls 'personalisation' is actually 'historical pattern matching'. It's not personalised to the person I am today. It's personalised to the person I was when I first signed up."},
    {"id": 70, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "I know exactly what Spotify knows about me because I can see my listening history. What it doesn't know: my curiosity, my mood, my intention, my openness to something new. None of that is captured."},
    {"id": 71, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "Asked Spotify support why my recommendations are so repetitive. They said 'listen to more music across different genres'. I'm literally asking them to help me do that and they're telling me to do it myself."},
    {"id": 72, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "The irony is that I'm paying for Spotify Premium partly for better discovery and the free YouTube algorithm discovers better music for me. No subscription required on YouTube."},
    {"id": 73, "src": "App Store", "date": "Apr 2026", "rating": 2, "text": "Three years ago Spotify's discovery was so good it felt like magic. Now it feels like it's just reading my listening history out loud back to me. The magic is completely gone."},
    {"id": 74, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Spotify should learn from how good YouTube is at discovery. YouTube regularly shows me things I didn't know I wanted to see. Spotify shows me things I already know I like."},
    {"id": 75, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "The 'Made For You' section is misnamed. It should be called 'Made From Your Past' because it reflects nothing about my current interests or where I want to go musically."},
    {"id": 76, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "Spent 2 hours on Spotify trying to find new music to love. Found nothing. Spent 20 minutes on a music subreddit and got 15 new artists I'm now obsessed with. Why is Reddit better at this than Spotify?"},
    {"id": 77, "src": "Reddit", "date": "May 2026", "rating": None, "text": "The algorithm seems to have a strong bias toward popular music within your genre. So you get the most-streamed version of your taste, not the most interesting version of it."},
    {"id": 78, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "I would pay extra for a Spotify tier that included human curation alongside the algorithm. A real music expert who knows my taste recommending things the algorithm would never surface."},
    {"id": 79, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The algorithm treats all my listening equally. But 80% of my listening is background music I barely pay attention to. The 20% I'm really engaged with should drive discovery, not the 80%."},
    {"id": 80, "src": "App Store", "date": "May 2026", "rating": 1, "text": "Every recommendation Spotify shows me, I've either heard before or could have predicted it would show me. There are no surprises. Discovery requires surprise. Spotify has eliminated surprise."},
    {"id": 81, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "The algorithm learned I like Radiohead. Cool. It doesn't know I want to find music that has Radiohead's emotional intensity but comes from a completely different genre. That's actual discovery."},
    {"id": 82, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "Feature I want desperately: describe what you're in the mood for in words, and Spotify finds it. 'Something melancholy but with energy.' Simple concept. Should be possible with AI. Doesn't exist."},
    {"id": 83, "src": "Play Store", "date": "Apr 2026", "rating": 2, "text": "Spotify could use conversational AI to understand what kind of discovery experience I want right now. Instead it just patterns-matches my past behaviour. Big missed opportunity."},
    {"id": 84, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "I've noticed that if I play any music my girlfriend shows me, my algorithm gets corrupted for weeks. The system has no concept of 'I'm listening to this for her, not for me'."},
    {"id": 85, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "The fundamental problem: Spotify is great at telling me what I like. Terrible at telling me what I would like if I knew it existed. Those are completely different problems requiring different solutions."},
    {"id": 86, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "I've been on Spotify Premium for 6 years. I trusted the algorithm completely in year 1-2. Now I trust it for nothing related to discovery. I only use Spotify to play music I found elsewhere."},
    {"id": 87, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "The algorithm needs a 'discovery confidence score'. If it's been a long time since I found a new artist I kept listening to, it should know something is wrong and change its approach."},
    {"id": 88, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "My Discover Weekly this week: 18 songs I've heard before, 7 songs by artists I already follow, 5 songs that are completely wrong for my taste. Zero actual discoveries. Zero."},
    {"id": 89, "src": "App Store", "date": "Apr 2026", "rating": 1, "text": "Cancelled Premium and switched to free for 3 months specifically to reset my algorithm. Didn't work. Same recommendations when I came back. The memory is apparently permanent."},
    {"id": 90, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "Good app, terrible discovery. I've given up on the algorithmic features and just use the search and human-curated playlists. The human curators at Spotify do a better job than the algorithm."},
    {"id": 91, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "Every time I play music at a social event, Spotify for the next 2 weeks thinks I love whatever genre was popular at that party. There's no way to exclude social listening from my profile."},
    {"id": 92, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "Real talk: the best music discovery tool in 2026 is asking an AI chatbot 'I like X and Y, what should I listen to?'. The AI gives better recommendations than Spotify does. That's embarrassing for Spotify."},
    {"id": 93, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "Spotify has access to every song ever recorded and knows exactly what I listen to. It should be the greatest discovery engine ever built. Instead it's worse at discovery than a random shuffle of my own library."},
    {"id": 94, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "After 4 years I know the algorithm's patterns. It recommends X → I listen → more X. It never breaks out of this loop. There's no curiosity in the algorithm. It's completely incurious about what else I might love."},
    {"id": 95, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The word I'd use for Spotify's discovery algorithm is 'timid'. It never takes risks. It never surprises. It calculates what will probably land well and serves that, every time. No personality."},
    {"id": 96, "src": "App Store", "date": "May 2026", "rating": 2, "text": "What I need: Spotify to say 'I notice you've been in a musical rut for 3 months. Want me to shake things up?' It has all the data to know this. It never acts on it."},
    {"id": 97, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "The worst part of bad recommendations isn't the bad recommendation. It's that I can't explain to the algorithm why it was wrong. No feedback mechanism beyond like/skip exists."},
    {"id": 98, "src": "Play Store", "date": "Feb 2026", "rating": 3, "text": "Spotify knows I like melancholy music. It doesn't know the difference between 'melancholy because of the lyrics' and 'melancholy because of the instrumentation'. These lead to completely different discoveries."},
    {"id": 99, "src": "Play Store", "date": "Mar 2026", "rating": 2, "text": "I've made peace with the fact that Spotify isn't a discovery service for me anymore. It's a playback service. I discover music on YouTube and Bandcamp and then come to Spotify to listen."},
    {"id": 100, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "The algorithm learns your skips and your likes but it never learns your curiosity. Curiosity is what drives discovery. Since the algorithm can't model curiosity, discovery is impossible at scale."},
    {"id": 101, "src": "Reddit", "date": "May 2026", "rating": None, "text": "Been saying this for years: Spotify needs a 'discovery mode' that is completely separate from normal listening. Everything played in discovery mode doesn't affect your main algorithm profile."},
    {"id": 102, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "I'm a music teacher. I want to explore genres I know nothing about to broaden my perspective. Spotify's algorithm assumes I only want more of what I already know. Completely wrong assumption."},
    {"id": 103, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "The 'Users also like' feature on artist pages is the only discovery tool that still semi-works for me. Everything else in 'Made For You' is stuck in 2022 for my account."},
    {"id": 104, "src": "App Store", "date": "Mar 2026", "rating": 2, "text": "I'd love if Spotify had a 'musical journey' feature — you pick a starting point and an ending point (genre-wise) and it builds you a playlist that gradually transitions between them. Pure discovery."},
    {"id": 105, "src": "App Store", "date": "Apr 2026", "rating": 1, "text": "The algorithm has completely stopped evolving for me. It found a formula that keeps me listening and it just keeps running that formula. I'm bored. I'm going to cancel."},
    {"id": 106, "src": "Play Store", "date": "May 2026", "rating": 2, "text": "Went on holiday for 2 weeks and listened to local music. Came back and my algorithm was completely wrecked for a month. The system can't understand 'temporary context shift'."},
    {"id": 107, "src": "Play Store", "date": "Jan 2026", "rating": 3, "text": "I miss when music discovery on Spotify felt like finding treasure. Now it feels like being shown the same treasure I already found, forever. The sense of musical adventure is completely gone."},
    {"id": 108, "src": "Reddit", "date": "Jan 2026", "rating": None, "text": "The algorithm gives me what I will tolerate, not what I will love. There's a massive gap between 'music I'll let play' and 'music that changes my life'. Spotify has optimised for the former."},
    {"id": 109, "src": "Reddit", "date": "Feb 2026", "rating": None, "text": "Feature request: 'Musical MBTI' — a periodic quiz that resets the algorithm's understanding of who I am. Because who I was 3 years ago and who I am now musically are very different people."},
    {"id": 110, "src": "Spotify Community", "date": "Mar 2026", "rating": None, "text": "I've started maintaining a separate Apple Music account just for exploration, so my Spotify algorithm doesn't get polluted. This is ridiculous. I shouldn't need two streaming services."},
    {"id": 111, "src": "Spotify Community", "date": "Apr 2026", "rating": None, "text": "The biggest problem: Spotify doesn't know the difference between 'music I like' and 'music I'm comfortable with'. The former should drive discovery. The latter kills it."},
    {"id": 112, "src": "App Store", "date": "May 2026", "rating": 2, "text": "Honest feedback: Spotify is winning at retention (keeping me listening) but losing at satisfaction (making my musical life richer). These are different goals and right now only one is being achieved."},
    {"id": 113, "src": "App Store", "date": "Jan 2026", "rating": 2, "text": "What if Spotify let you set a 'discovery budget'? Like, 30% of every playlist has to be music you've never heard before. And you can adjust that percentage. Simple, controllable, meaningful."},
    {"id": 114, "src": "Play Store", "date": "Feb 2026", "rating": 2, "text": "I get better music discovery from reading music journalism online than from Spotify's algorithm. Human writers can explain why something is interesting. Algorithms just pattern-match."},
    {"id": 115, "src": "Play Store", "date": "Mar 2026", "rating": 3, "text": "The algorithm is basically doing collaborative filtering: people like you also listened to this. But people like me are also in a musical rut. I need recommendations from people unlike me."},
    {"id": 116, "src": "Reddit", "date": "Apr 2026", "rating": None, "text": "Imagine if Spotify could say: 'This song connects to what you love about X but opens a door to genre Y that you've never explored.' That's actual discovery. The algorithm cannot do this."},
    {"id": 117, "src": "Reddit", "date": "May 2026", "rating": None, "text": "The algorithm has never once shown me something that made me think 'how did it know I'd love this?'. That moment of surprise is what discovery feels like. Spotify has stopped producing it."},
    {"id": 118, "src": "Spotify Community", "date": "Jan 2026", "rating": None, "text": "What I want Spotify to be: a guide who knows where I've been and can intelligently suggest where to go next. What it is: a map that only shows places I've already visited."},
    {"id": 119, "src": "Spotify Community", "date": "Feb 2026", "rating": None, "text": "I asked my friend who's a music obsessive to make me a playlist. It was 30 songs, 25 of which I'd never heard, all of which I loved. Spotify has never produced anything remotely close to this."},
    {"id": 120, "src": "App Store", "date": "Mar 2026", "rating": 1, "text": "Three words summarise my experience with Spotify's discovery in 2026: predictable, safe, boring. I'm a music lover. I want to be surprised, challenged, and moved. The algorithm does none of this."},
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
    # Sample 40 reviews for API to stay within token limits
    sample = random.sample(reviews_list, min(40, len(reviews_list)))
    block = "\n".join([
        f'[{i+1}] {r["src"]}: "{r["text"][:100]}"'
        for i, r in enumerate(sample)
    ])
    prompt = f"""You are a senior product researcher at Spotify. Analyze these {len(sample)} user reviews (sampled from {len(reviews_list)} total) about music discovery. Return ONLY raw valid JSON — no markdown, no code fences. Keep values concise.

REVIEWS:
{block}

Return this JSON (max 4 items per array):
{{
  "headline": "One insight under 15 words",
  "discovery_pct": "X% mention discovery issues",
  "sentiment": {{"negative": N, "neutral": N, "positive": N}},
  "barriers": [{{"title": "Short title", "desc": "One sentence", "severity": "Critical|High|Medium"}}],
  "frustrations": [{{"title": "Short title", "desc": "One sentence", "evidence": "5 words max"}}],
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
    except json.JSONDecodeError:
        st.error("JSON parse error — please try again.")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

def badge(level):
    colors = {"Critical": "#ff4444", "High": "#ff8c00", "Medium": "#1DB954"}
    c = colors.get(level, "#1DB954")
    return f'<span style="background:{c};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{level}</span>'

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:rgba(29,185,84,0.15);border:1px solid #1DB954;border-radius:10px;padding:14px 20px;margin-bottom:20px;">
  <p style="color:#1DB954;font-size:11px;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 4px;">
    🎵 AI RESEARCH TOOL &nbsp;·&nbsp; Real reviews &nbsp;·&nbsp; App Store · Play Store · Reddit · Spotify Community
  </p>
  <h1 style="color:white;margin:0 0 4px;font-size:2rem;">Echo Decoder</h1>
  <p style="color:#aaa;margin:0;font-size:14px;">AI-powered analysis of real Spotify user feedback — surfaces music discovery barriers at scale</p>
</div>
""", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 3])

with col_left:
    src_filter = st.selectbox("Filter by source", SOURCES)
    filtered = ALL_REVIEWS if src_filter == "All sources" else [r for r in ALL_REVIEWS if r["src"] == src_filter]

    st.markdown(f'<p style="color:#1DB954;font-size:13px;font-weight:600;">📊 {len(ALL_REVIEWS)} reviews loaded · Showing {len(filtered)}</p>', unsafe_allow_html=True)

    review_container = st.container(height=400)
    with review_container:
        for r in filtered[:50]:  # Show first 50 for performance
            stars = ("★" * r["rating"] + "☆" * (5 - r["rating"])) if r["rating"] else "—"
            st.markdown(f"""
<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;padding:10px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:5px;flex-wrap:wrap;gap:3px;">
    <span style="background:#2a2a2a;color:#aaa;padding:1px 8px;border-radius:10px;font-size:11px;">{r['src']}</span>
    <span style="color:#f39c12;font-size:11px;">{stars}</span>
    <span style="color:#555;font-size:11px;">{r['date']}</span>
  </div>
  <p style="color:#ddd;font-size:12px;margin:0;line-height:1.6;">{r['text']}</p>
</div>""", unsafe_allow_html=True)
    if len(filtered) > 50:
        st.caption(f"Showing 50 of {len(filtered)} reviews")

    st.divider()
    with st.expander("➕ Add a review"):
        new_src = st.selectbox("Source", ["App Store", "Play Store", "Reddit", "Spotify Community"], key="nsrc")
        new_text = st.text_area("Paste review", placeholder="Paste a user review here...", height=80, key="ntxt")
        if st.button("Add") and new_text.strip():
            ALL_REVIEWS.append({"id": len(ALL_REVIEWS)+1, "src": new_src, "date": "Jun 2026", "rating": 3, "text": new_text.strip()})
            st.success("Added!")
            st.rerun()

    st.divider()
    if st.button(f"✨ Analyze {len(ALL_REVIEWS)} reviews with AI", type="primary", use_container_width=True):
        with st.spinner("Analyzing 40 sampled reviews with Llama 3.3..."):
            result = analyze(ALL_REVIEWS)
            if result:
                st.session_state["analysis"] = result
                st.rerun()

with col_right:
    if "analysis" not in st.session_state:
        st.markdown("""
<div style="background:#1a1a1a;border:2px dashed #333;border-radius:12px;padding:3rem;text-align:center;margin-top:1rem;">
  <p style="font-size:3rem;margin:0 0 12px;">📊</p>
  <p style="color:#aaa;font-size:15px;font-weight:500;margin:0 0 6px;">Click "Analyze reviews" to run AI analysis</p>
  <p style="color:#555;font-size:13px;margin:0;">Samples 40 reviews · Answers 6 PM research questions<br>Powered by Groq · Llama 3.3 70B · Free</p>
</div>""", unsafe_allow_html=True)
    else:
        a = st.session_state["analysis"]

        st.markdown(f"""
<div style="background:rgba(29,185,84,0.12);border:1px solid #1DB954;border-radius:8px;padding:14px 18px;margin-bottom:14px;">
  <p style="color:#1DB954;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin:0 0 5px;">KEY FINDING</p>
  <p style="color:#1DB954;font-size:17px;font-weight:600;margin:0 0 6px;line-height:1.4;">{a.get('headline','')}</p>
  <p style="color:#1DB954;font-size:12px;opacity:0.75;margin:0;">{a.get('discovery_pct','')}</p>
</div>""", unsafe_allow_html=True)

        sent = a.get("sentiment", {})
        s1, s2, s3 = st.columns(3)
        s1.metric("😤 Negative", f"{sent.get('negative', 0)}%")
        s2.metric("😐 Neutral", f"{sent.get('neutral', 0)}%")
        s3.metric("😊 Positive", f"{sent.get('positive', 0)}%")

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🚫 Barriers", "👥 Segments", "😤 Frustrations", "💡 Needs", "🎯 Behaviors", "🔄 Repeat"])

        with tab1:
            st.markdown("**Why users struggle to discover new music**")
            for b in a.get("barriers", []):
                st.markdown(f"**{b['title']}** {badge(b['severity'])}", unsafe_allow_html=True)
                st.caption(b['desc'])
                st.divider()

        with tab2:
            st.markdown("**User segments and their challenges**")
            for s in a.get("segments", []):
                st.markdown(f"**{s['name']}** — *{s['size']}*")
                st.caption(s['desc'])
                st.markdown(f"⚠️ {s['pain']}")
                st.divider()

        with tab3:
            st.markdown("**Most common frustrations**")
            for f in a.get("frustrations", []):
                st.markdown(f"**{f['title']}**")
                st.caption(f['desc'])
                if f.get('evidence'):
                    st.markdown(f"> *{f['evidence']}*")
                st.divider()

        with tab4:
            st.markdown("**Unmet needs across reviews**")
            for n in a.get("unmet_needs", []):
                st.markdown(f"**{n['need']}** {badge(n['priority'])}", unsafe_allow_html=True)
                st.caption(n['desc'])
                st.divider()

        with tab5:
            st.markdown("**What behaviors users are trying to achieve**")
            for beh in a.get("behaviors", []):
                st.markdown(f"**{beh['goal']}**")
                st.caption(beh['desc'])
                st.divider()

        with tab6:
            st.markdown("**Why users repeat-listen instead of explore**")
            for rc in a.get("repeat_causes", []):
                st.markdown(f"**{rc['cause']}**")
                st.caption(rc['desc'])
                st.divider()

        st.markdown(f"""
<div style="background:rgba(255,180,0,0.1);border:1px solid #ffb800;border-radius:8px;padding:14px 18px;margin-top:10px;">
  <p style="color:#ffb800;font-size:10px;text-transform:uppercase;margin:0 0 5px;">🔍 ROOT CAUSE</p>
  <p style="color:#fff;font-size:13px;margin:0;line-height:1.75;">{a.get('root_cause','')}</p>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:#1a1a1a;border:1px solid #1DB954;border-radius:8px;padding:14px 18px;margin-top:10px;">
  <p style="color:#1DB954;font-size:10px;text-transform:uppercase;margin:0 0 5px;">🎯 RECOMMENDED FOCUS SEGMENT</p>
  <p style="color:#fff;font-size:13px;margin:0;line-height:1.75;">{a.get('focus_segment','')}</p>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear & re-analyze"):
            del st.session_state["analysis"]
            st.rerun()
