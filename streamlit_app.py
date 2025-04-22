"""
Streamlit application for Deckoviz Personal Painter

This app provides a web interface for the Personal Painter feature,
allowing users to input their emotions and generate personalized art experiences.
"""

import os
import json
import asyncio
import streamlit as st
from PIL import Image
from datetime import datetime
import base64
from io import BytesIO

# Import Personal Painter
from deckoviz_ai.personal_painter.personal_painter import (
    PersonalPainter, 
    process_emotion_and_generate_art,
    EMOTION_TO_COLOR_MAP
)

# Set page configuration
st.set_page_config(
    page_title="Deckoviz Personal Painter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .emotion-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .prompt-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
        font-style: italic;
    }
    .history-item {
        padding: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_emotion_color(emotion):
    """Return a color based on the emotion"""
    emotion_colors = {
        "joy": "#FFC107",       # Yellow
        "sadness": "#0D47A1",   # Deep Blue
        "anger": "#D32F2F",     # Red
        "fear": "#455A64",      # Dark Grey
        "disgust": "#558B2F",   # Green
        "surprise": "#7B1FA2",  # Purple
        "neutral": "#607D8B"    # Blue Grey
    }
    return emotion_colors.get(emotion, "#607D8B")

def get_emotion_emoji(emotion):
    """Return an emoji based on the emotion"""
    emotion_emojis = {
        "joy": "😊",
        "sadness": "😢",
        "anger": "😠",
        "fear": "😨",
        "disgust": "🤢",
        "surprise": "😲",
        "neutral": "😐"
    }
    return emotion_emojis.get(emotion, "🎨")

async def async_process_input(user_input):
    """Process user input asynchronously"""
    # Initialize the Personal Painter
    painter = PersonalPainter(
        api_key=os.getenv("STABILITY_API_KEY"),
        image_dir="output/personal_painter"
    )
    
    # Process the input and generate art
    result = await process_emotion_and_generate_art(painter, user_input)
    return result

def run_async(coroutine):
    """Run an async function synchronously"""
    import asyncio
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(coroutine)
    loop.close()
    return result

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# App header
st.markdown("<h1 class='main-header'>Deckoviz Personal Painter</h1>", unsafe_allow_html=True)
st.markdown(
    "Transform your emotions into art with Deckoviz's Personal Painter. "
    "Enter your thoughts and feelings to create a personalized artistic experience."
)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    # User input section
    st.markdown("<h2 class='sub-header'>Express Yourself</h2>", unsafe_allow_html=True)
    user_input = st.text_area(
        "Share your thoughts, feelings, or experiences...",
        height=150,
        placeholder="For example: I'm feeling really excited about my upcoming vacation to the mountains..."
    )
    
    submit_button = st.button("Generate Art", type="primary")
    
    # Process input when button is clicked
    if submit_button and user_input:
        with st.spinner("Analyzing your emotions and creating art..."):
            # Process the input
            result = run_async(async_process_input(user_input))
            
            # Add to history
            st.session_state.history.append({
                "input": user_input,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display results
            emotion_data = result["processed"]["emotion"]
            art_data = result["art"]
            
            # Emotion analysis results
            primary_emotion = emotion_data["primary_emotion"]
            confidence = emotion_data["confidence"]
            emotion_color = get_emotion_color(primary_emotion)
            emotion_emoji = get_emotion_emoji(primary_emotion)
            
            st.markdown(f"<h2 class='sub-header'>Emotional Analysis</h2>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='emotion-box' style='background-color: {emotion_color}; color: white;'>"
                f"<h3>{emotion_emoji} {primary_emotion.capitalize()}</h3>"
                f"<p>Confidence: {confidence:.2f}</p>"
                "</div>",
                unsafe_allow_html=True
            )
            
            # Art prompt
            st.markdown("<h2 class='sub-header'>Art Prompt</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='prompt-box'>{art_data['prompt']}</div>", unsafe_allow_html=True)
            
            # In a real implementation, we would display the generated image here
            st.markdown("<h2 class='sub-header'>Visual Representation</h2>", unsafe_allow_html=True)
            
            # For now, we'll just show a placeholder or mock image
            # In the future, this could display the actual generated image
            st.info(
                "In a production environment, this would display the AI-generated image. "
                "Currently using a placeholder since image generation is mocked."
            )
            
            # Create a simple placeholder image based on the emotion
            def create_color_image(emotion):
                # Get a color theme for the emotion
                color_themes = EMOTION_TO_COLOR_MAP.get(emotion, ["colorful"])
                import random
                color_theme = random.choice(color_themes)
                
                # Create a simple gradient image
                width, height = 512, 512
                from PIL import Image, ImageDraw
                image = Image.new("RGB", (width, height), "#FFFFFF")
                draw = ImageDraw.Draw(image)
                
                if color_theme == "vibrant" or color_theme == "colorful" or color_theme == "rainbow":
                    # Create rainbow gradient
                    colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]
                    for i, color in enumerate(colors):
                        draw.rectangle([0, i * height // len(colors), width, (i + 1) * height // len(colors)], fill=color)
                else:
                    # Create gradient based on emotion color
                    base_color = get_emotion_color(emotion)
                    # Convert hex to RGB
                    r = int(base_color[1:3], 16)
                    g = int(base_color[3:5], 16)
                    b = int(base_color[5:7], 16)
                    
                    for y in range(height):
                        # Create a gradient effect
                        factor = y / height
                        r_new = int(r * (1 - factor) + 255 * factor)
                        g_new = int(g * (1 - factor) + 255 * factor)
                        b_new = int(b * (1 - factor) + 255 * factor)
                        draw.line([(0, y), (width, y)], fill=(r_new, g_new, b_new))
                
                return image
            
            # Create and display placeholder image
            img = create_color_image(primary_emotion)
            st.image(img, caption=f"Placeholder for: {art_data['prompt']}", use_column_width=True)

with col2:
    # History/sidebar section
    st.markdown("<h2 class='sub-header'>Your Art History</h2>", unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("Your art creation history will appear here after you generate your first piece.")
    else:
        # Display history in reverse order (newest first)
        for item in reversed(st.session_state.history):
            primary_emotion = item["result"]["processed"]["emotion"]["primary_emotion"]
            emotion_emoji = get_emotion_emoji(primary_emotion)
            timestamp = datetime.fromisoformat(item["timestamp"]).strftime("%H:%M:%S")
            
            st.markdown(
                f"<div class='history-item'>"
                f"<p><strong>{timestamp}</strong> {emotion_emoji} {primary_emotion.capitalize()}</p>"
                f"<p><em>{item['input'][:50]}{'...' if len(item['input']) > 50 else ''}</em></p>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    # Settings
    st.markdown("<h2 class='sub-header'>Settings</h2>", unsafe_allow_html=True)
    
    # API Key input (in a real app, this should be more secure)
    api_key = st.text_input(
        "Stability API Key (optional)", 
        value=os.getenv("STABILITY_API_KEY", ""),
        type="password",
        help="For image generation using Stability AI. Leave empty to use mock images."
    )
    
    if api_key:
        os.environ["STABILITY_API_KEY"] = api_key
    
    # Clear history button
    if st.button("Clear History"):
        st.session_state.history = []
        st.success("History cleared!")

# Footer
st.markdown("---")
st.markdown(
    "Deckoviz Personal Painter | AI-powered Smart Art Frame | "
    "© 2025 Deckoviz"
)

if __name__ == "__main__":
    # This allows the app to be run with `streamlit run streamlit_app.py`
    pass
