import streamlit as st
import logging
from gtts import gTTS
import base64
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Hugging Face model and tokenizer names
model_name = 'TresorB/TshilubaEnglishTranslationModel'
tokenizer_name = 'TresorB/TshilubaEnglishTranslationTokenizer'

# Function to load the model from Hugging Face
@st.cache_resource
def load_model():
    try:
        from transformers import MarianMTModel
        model = MarianMTModel.from_pretrained(model_name)
        return model
    except ImportError as e:
        logger.error(f"Failed to import MarianMTModel: {e}")
        st.error("Failed to import the model. Please check if the transformers library is correctly installed.")
        return None
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        st.error("Failed to load the model. Please check the logs for more details.")
        return None

# Function to load the tokenizer from Hugging Face
@st.cache_resource
def load_tokenizer():
    try:
        from transformers import MarianTokenizer
        tokenizer = MarianTokenizer.from_pretrained(tokenizer_name)
        return tokenizer
    except ImportError as e:
        logger.error(f"Failed to import MarianTokenizer: {e}")
        st.error("Failed to import the tokenizer. Please check if the transformers library is correctly installed.")
        return None
    except Exception as e:
        logger.error(f"Failed to load tokenizer: {e}")
        st.error("Failed to load the tokenizer. Please check the logs for more details.")
        return None

# Streamlit App
st.title("MarianMT Model Translation")

# Load Model and Tokenizer
model = load_model()
tokenizer = load_tokenizer()
if model and tokenizer:
    st.success("Model and Tokenizer loaded successfully from Hugging Face.")
else:
    st.error("Failed to load Model and Tokenizer.")

# Translation interface
st.subheader("Translate Tshiluba to English")

tshiluba_text = st.text_area("Enter Tshiluba text to translate")
if st.button("Translate"):
    if tshiluba_text and model and tokenizer:
        with st.spinner("Translating..."):
            # Tokenize input
            inputs = tokenizer(tshiluba_text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)

            # Generate translation
            translated = model.generate(**inputs)

            # Decode the output
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            st.success(f"Translated text: {translated_text}")
            
            # Convert translated text to speech
            tts = gTTS(translated_text)
            tts.save("translated_audio.mp3")

            # Display audio player
            audio_file = open("translated_audio.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

            # Optionally provide a download link
            def get_binary_file_downloader_html(bin_file, file_label='File'):
                with open(bin_file, 'rb') as f:
                    data = f.read()
                bin_str = base64.b64encode(data).decode()
                href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
                return href

            st.markdown(get_binary_file_downloader_html("translated_audio.mp3", 'Download translated audio'), unsafe_allow_html=True)
    else:
        st.warning("Please enter some Tshiluba text to translate.")


