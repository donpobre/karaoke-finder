import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to True for this static version.
_RELEASE = True

# Declare the component
# We point to the local directory where index.html will live.
parent_dir = os.path.dirname(os.path.abspath(__file__))
_component_func = components.declare_component(
    "youtube_voice_player",
    path=parent_dir,
)

def youtube_voice_player(video_id, key=None):
    """
    Create a new instance of the "youtube_voice_player".
    
    Parameters
    ----------
    video_id: str
        The YouTube Video ID to play.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
        
    Returns
    -------
    dict
        A dictionary with events: e.g. {"type": "ended"} or {"type": "voice", "command": "next"}
    """
    component_value = _component_func(video_id=video_id, key=key, default=None)
    return component_value
