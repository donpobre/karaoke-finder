import streamlit as st
from player_component import youtube_voice_player
from youtubesearchpython import VideosSearch
import re

st.set_page_config(page_title="Karaoke AI", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 10% 20%, rgba(75, 0, 130, 0.4) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(180, 0, 100, 0.4) 0px, transparent 50%);
        background-attachment: fixed;
        color: white;
    }
    
    /* Move title to top and make content wider */
    .main .block-container {
        padding-top: -1rem;
        max-width: 95%;
        margin-top: -1rem!important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #333;
    }
    
    /* Sidebar Title */
    [data-testid="stSidebar"] h1 {
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Top Header */
    header[data-testid="stHeader"] {
        background-color: transparent;
        margin-top: -1rem;
    }

    /* Queue Items */
    .queue-item {
        padding: 10px;
        border-bottom: 1px solid #222;
        color: #aaa;
        font-size: 14px;
    }
    .queue-item.active {
        background: linear-gradient(90deg, rgba(50,50,50,0.5), transparent);
        color: white;
        border-left: 3px solid #6a11cb;
    }
    .queue-number {
        font-weight: bold;
        margin-right: 10px;
        color: #555;
    }
    .queue-item.active .queue-number {
        color: #fff;
    }

    /* Buttons */
    .stButton button {
        background-color: #222;
        color: white;
        border: 1px solid #444;
        border-radius: 5px;
    }
    .stButton button:hover {
        border-color: #6a11cb;
        color: #6a11cb;
    }
    
    /* Specific fix for the X remove buttons in queue */
    [data-testid="stSidebar"] button[key^="rem_"] {
        width: 30px;
        height: 30px;
        min-width: 30px;
        min-height: 30px;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #888;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: white;
        border-bottom: 2px solid #6a11cb;
    }
    
    /* Make iframe component taller */
    iframe {
        min-height: 1000px !important;
    }

    /* ===== MOBILE RESPONSIVE STYLES ===== */
    @media (max-width: 768px) {
        /* Hide sidebar by default on mobile */
        [data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: -21rem;
        }
        
        /* Show sidebar when expanded */
        [data-testid="stSidebar"][aria-expanded="true"] {
            margin-left: 0;
        }
        
        /* Ensure hamburger menu is visible and styled */
        [data-testid="collapsedControl"] {
            display: flex !important;
            background-color: #6a11cb !important;
            color: white !important;
            border-radius: 5px;
            padding: 8px;
            margin: 10px;
            z-index: 999;
        }
        
        /* Adjust main content on mobile */
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Make tabs more compact on mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 14px;
            padding: 8px 12px;
        }
        
        /* Adjust iframe height for mobile */
        iframe {
            min-height: 500px !important;
        }
        
        /* Make title smaller on mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        
        /* Adjust queue items for mobile */
        .queue-item {
            font-size: 12px;
            padding: 8px;
        }
    }
    
    /* Extra small devices (phones in portrait) */
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        h1 {
            font-size: 1.2rem !important;
        }
        
        iframe {
            min-height: 400px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def extract_video_id(url_or_id):
    """Extracts YouTube Video ID from URL or returns the ID itself."""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) == 11:
        return url_or_id
    return None

def search_youtube(query, max_results=5):
    videos_search = VideosSearch(query, limit=max_results)
    return videos_search.result()['result']

# --- Session State Initialization ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = [
        {"title": "Bohemian Rhapsody - Queen", "id": "fJ9rUzIMcZQ"}        
    ]

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

if 'processed_voice_commands' not in st.session_state:
    st.session_state.processed_voice_commands = set()

# --- Sidebar: Playlist Management ---
st.sidebar.title("🎵 Playlist")

# Manual Add
new_song_input = st.sidebar.text_input("Add Song (URL or ID)")
if st.sidebar.button("Add to Queue"):
    vid_id = extract_video_id(new_song_input)
    if vid_id:
        st.session_state.playlist.append({"title": f"Song {vid_id}", "id": vid_id})
        st.sidebar.success("Added!")
    else:
        st.sidebar.error("Invalid URL/ID")

st.sidebar.markdown("---")
st.sidebar.markdown("### Queue")
for i, song in enumerate(st.session_state.playlist):
    active_class = "active" if i == st.session_state.current_index else ""
    title = song['title']
    if "-" in title:
        parts = title.split("-", 1)
        song_title = parts[0].strip()
        artist = parts[1].strip()
    else:
        song_title = title
        artist = ""
    
    # Use columns to put text and button side-by-side
    col1, col2 = st.sidebar.columns([0.85, 0.15], vertical_alignment="center")
    
    with col1:
        st.markdown(f"""
        <div class="queue-item {active_class}" style="border:none; padding: 5px 0;">
            <span class="queue-number">{i+1}</span>
            <span style="font-weight:500">{song_title}</span><br>
            <span style="font-size:12px; margin-left: 20px; opacity: 0.7">{artist}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Only show remove button for non-active songs
        if i != st.session_state.current_index:
            if st.button("✖", key=f"rem_{i}", help=f"Remove {title}"):
                 st.session_state.playlist.pop(i)
                 if i < st.session_state.current_index:
                     st.session_state.current_index -= 1
                 st.rerun()

# --- Main Logic ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("🎤 Karaoke Finder")
with col2:
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    voice_enabled = st.checkbox("🎤 Voice Control", value=False, key="voice_toggle")

tab1, tab2 = st.tabs(["Player", "Search Songs"])

with tab1:
    # Get current song
    if 0 <= st.session_state.current_index < len(st.session_state.playlist):
        current_song = st.session_state.playlist[st.session_state.current_index]
        
        # --- Next Up Preview ---
        next_index = st.session_state.current_index + 1
        if next_index < len(st.session_state.playlist):
            next_song = st.session_state.playlist[next_index]
            st.info(f"**Next Up:** {next_song['title']}")
        else:
            st.info("**Next Up:** End of Playlist")

        # --- Player Component ---
        event = youtube_voice_player(video_id=current_song['id'], key="main_player")

        # --- Event Handling ---
        if event:
            event_type = event.get("type")
            
            if event_type == "ended":
                if st.session_state.current_index < len(st.session_state.playlist) - 1:
                    st.session_state.current_index += 1
                    st.rerun()
                else:
                    st.warning("Playlist finished!")
            
            elif event_type == "voice":
                command = event.get("command")
                if command == "next":
                    if st.session_state.current_index < len(st.session_state.playlist) - 1:
                        st.session_state.current_index += 1
                        st.rerun()
                    else:
                        st.toast("No more songs!")
                elif command == "search":
                    query = event.get("query")
                    # Create a unique identifier for this voice command
                    command_id = f"search_{query}_{event.get('timestamp', '')}"
                    
                    # Check if we've already processed this command
                    if command_id in st.session_state.processed_voice_commands:
                        # Already processed, skip to prevent infinite loop
                        pass
                    else:
                        st.toast(f"Voice Search: {query}")
                        try:
                            # Perform search and add first result
                            results = search_youtube(query + " karaoke", max_results=1)
                            if results:
                                video = results[0]
                                # Play Immediately Logic
                                st.session_state.playlist.insert(st.session_state.current_index + 1, {"title": video['title'], "id": video['id']})
                                st.session_state.current_index += 1
                                # Mark this command as processed
                                st.session_state.processed_voice_commands.add(command_id)
                                st.toast(f"Playing: {video['title']}")
                                st.rerun()
                            else:
                                st.toast("No results found")
                                st.session_state.processed_voice_commands.add(command_id)
                        except Exception as e:
                            st.error(f"Search failed: {e}")
                            st.session_state.processed_voice_commands.add(command_id)

    else:
        st.write("Playlist is empty. Add some songs from the Search tab!")

with tab2:
    st.subheader("Search YouTube")
    
    with st.form(key="search_form", clear_on_submit=False):
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background: linear-gradient(90deg, #ff4ec7, #7a2ff7);
                color: white;
                padding: 0.6rem 1.2rem;
                border-radius: 12px;
                border: none;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: 0.3s ease;
            }
            div.stButton > button:first-child:hover {
                opacity: 0.85;
                transform: scale(1.03);
            }
            </style>
            """, unsafe_allow_html=True)        

        st.markdown("""
            <style>
            form button[kind="secondaryFormSubmit"] {
                background: linear-gradient(90deg, #ff4ec7, #7a2ff7);
                color: white !important;
                padding: 0.6rem 1.2rem;
                border-radius: 12px;
                border: none;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: 0.3s ease;
            }
            form button[kind="secondaryFormSubmit"]:hover {
                opacity: 0.9;
                transform: scale(1.03);
            }
            </style>
            """, unsafe_allow_html=True)
        search_query = st.text_input("Search for a song (e.g. 'Wonderwall karaoke')")
        search_button = st.form_submit_button("Search")
        
       
    
    if search_button:
        if search_query:
            with st.spinner("Searching..."):
                results = search_youtube(search_query)
                st.session_state.search_results = results
        else:
            st.warning("Please enter a search term.")

    # Display results from session state
    if 'search_results' in st.session_state and st.session_state.search_results:
        for video in st.session_state.search_results:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(video['thumbnails'][0]['url'])
            with col2:
                st.write(f"**{video['title']}**")
                st.write(f"Duration: {video['duration']}")
                
                # Use columns for buttons to keep them side-by-side
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("Play Now", key=f"play_{video['id']}"):
                        st.session_state.playlist.insert(st.session_state.current_index + 1, {"title": video['title'], "id": video['id']})
                        st.session_state.current_index += 1
                        st.rerun()
                with b_col2:
                    if st.button("Add to Queue", key=f"add_{video['id']}"):
                        st.session_state.playlist.append({"title": video['title'], "id": video['id']})
                        st.success(f"Added {video['title']}")
