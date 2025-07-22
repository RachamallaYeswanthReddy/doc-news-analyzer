import streamlit as st
import PyPDF2
from docx import Document
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="PDF + News Research Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------ CLEAN PROFESSIONAL STYLING ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base styles for dark mode - targeting the entire app */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: #1a1a1a; /* Black background */
        color: #e0e0e0; /* Light text */
    }

    /* Targeting the main content block for background consistency */
    .st-emotion-cache-1cyp85j {
        background-color: #1a1a1a; /* Black background */
    }

    /* Adjusting Streamlit widgets to be visible in dark mode */
    .st-ay.st-ax, .st-bf.st-bg {
        background-color: #2c2c2c; /* Darker input background */
        border: 1px solid #444444; /* Darker border */
        color: #e0e0e0; /* Light text in inputs */
    }
    .st-ay.st-ax:focus-within, .st-bf.st-bg:focus-within {
        border-color: #4CAF50; /* Green focus for better visibility */
        box-shadow: 0 0 0 1px #4CAF50;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #999999; /* Placeholder color for dark mode */
    }


    /* Main header */
    .main-header {
        text-align: center;
        padding: 2.5rem 0;
        margin-bottom: 2.5rem;
        background: #2c2c2c; /* Darker card background */
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); /* Stronger shadow */
        border: 1px solid #444444; /* Subtle dark border */
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f0f0f0; /* Lighter title color */
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    .main-subtitle {
        color: #c0c0c0; /* Lighter grey subtitle */
        font-size: 1.1rem;
    }

    /* Content sections */
    .content-section {
        background: #2c2c2c; /* Darker card background */
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
        border: 1px solid #444444;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f0f0f0; /* Lighter title color */
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    
    /* Labels for inputs */
    .stTextInput label, .stTextArea label, .stFileUploader label {
        font-weight: 600;
        color: #f0f0f0; /* White labels */
        margin-bottom: 0.5rem;
        display: block;
    }
    /* Specific styling for h3 elements used for 'Upload Files' and 'Add URLs' */
    .content-section h3 {
        color: #e0e0e0; /* Lighter heading color */
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
    }

    /* Status indicators */
    .status-success {
        background: #285a3c; /* Darker green */
        color: #a7f3d0; /* Lighter green text */
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #388e3c;
        margin-top: 10px;
    }

    .status-info {
        background: #1e3a8a; /* Darker blue */
        color: #93c5fd; /* Lighter blue text */
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #3b82f6;
        margin-top: 15px;
    }
    
    .stAlert {
        border-radius: 8px;
        color: #e0e0e0 !important; /* Ensure alert text is white */
    }
    .stAlert > div {
        background-color: #3a3a3a !important; /* Darker background for alerts */
        border-color: #555555 !important;
    }


    /* Buttons */
    .stButton > button {
        background: #4CAF50; /* Green primary button */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 1.8rem;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    }

    .stButton > button:hover {
        background: #388E3C; /* Darker green on hover */
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    /* Secondary buttons for quick questions */
    .stButton:first-of-type > button, .stButton:nth-of-type(2) > button {
        background: #3a3a3a; /* Darker background for secondary actions */
        color: #a7d0f3; /* Lighter blue text */
        border: 1px solid #555555;
        box-shadow: none;
    }
    .stButton:first-of-type > button:hover, .stButton:nth-of-type(2) > button:hover {
        background: #4a4a4a; /* Slightly lighter on hover */
        color: #88c0f3;
        transform: translateY(-1px);
        box-shadow: none;
    }

    /* File uploader custom text */
    .stFileUploader label p {
        font-size: 1rem;
        color: #c0c0c0; /* Lighter text for uploader instructions */
    }
    .stFileUploader {
        background: #3a3a3a; /* Darker background for uploader area */
        border-color: #555555;
    }


    /* Response box */
    .response-box {
        background: #1f3b4d; /* Darker blue for response box */
        border: 1px solid #2b5c77;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .response-box h4 {
        color: #88d0f1; /* Lighter blue for response title */
        margin-top: 0;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .response-content {
        color: #e0f2f7; /* Lighter text for response content */
        line-height: 1.7;
        font-size: 1.05rem;
    }
    
    /* Divider */
    hr {
        margin: 3rem 0;
        border-top: 1px solid #444444; /* Darker divider */
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

</style>
""", unsafe_allow_html=True)

if 'all_content' not in st.session_state:
    st.session_state.all_content = ""
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'quick_question' not in st.session_state:
    st.session_state.quick_question = ""


@st.cache_data(show_spinner=False)
def extract_pdf_text(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

@st.cache_data(show_spinner=False)
def extract_word_text(docx_file):
    try:
        doc = Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return ""

@st.cache_data(show_spinner=False)
def extract_url_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "input"]):
            tag.decompose()
        text = ' '.join(line.strip() for line in soup.get_text().splitlines() if line.strip())
        return text if len(text) > 100 else ""
    except requests.exceptions.RequestException as e:
        st.error(f"Network error or invalid URL: {url} - {e}")
        return ""
    except Exception as e:
        st.error(f"Error processing URL {url}: {e}")
        return ""

def ask_gemini(content, question, api_key):
    if not api_key:
        return "Error: Gemini API key is not provided."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
            As an AI assistant, analyze the following content and answer the question concisely and accurately.

            Content:
            {content[:70000]}

            Question: {question}

            Response:
            """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}. Please check your API key and try again."

def main():
    st.markdown("""
    <div class="main-header">
        <div class="main-title">📄 PDF + News Research Tool</div>
        <div class="main-subtitle">Analyze documents and web articles with AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-section">
        <div class="section-title">🔑 API Configuration</div>
    """, unsafe_allow_html=True)

    gemini_api_key = st.text_input(
        "Enter your Google Gemini API Key",
        type="password",
        placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        help="Get your API key from Google AI Studio (https://aistudio.google.com/app/apikey)",
        key="gemini_api_input"
    )

    if gemini_api_key:
        st.markdown('<div class="status-success">✅ API Key Configured</div>', unsafe_allow_html=True)
    else:
        st.warning("Please enter your Gemini API key to unlock content processing and Q&A features.")
        st.session_state.all_content = ""
        st.session_state.processed_files = []

    st.markdown('</div>', unsafe_allow_html=True)

    if gemini_api_key:
        st.markdown("""
        <div class="content-section">
            <div class="section-title">📂 Upload Content</div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h3>Upload Files</h3>", unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "Limit 200MB per file - PDF, DOCX",
                type=['pdf', 'docx'],
                accept_multiple_files=True,
                key="file_uploader"
            )

        with col2:
            st.markdown("<h3>Add URLs</h3>", unsafe_allow_html=True)
            urls_input = st.text_area(
                "Enter URLs (one per line)",
                height=150,
                placeholder="https://example.com/article\nhttps://news.example.com/another-story",
                key="url_input"
            )

        if st.button("📊 Process Content", use_container_width=True):
            if not uploaded_files and not urls_input.strip():
                st.error("Please upload files or enter URLs to process content.")
            else:
                content = ""
                files_processed = []

                existing_processed_names = [f.split('--- ')[1] if '--- ' in f else f for f in st.session_state.processed_files]

                with st.spinner("Processing content... This might take a moment for large inputs."):
                    if uploaded_files:
                        for file in uploaded_files:
                            if file.name not in existing_processed_names:
                                text = ""
                                if file.type == "application/pdf":
                                    text = extract_pdf_text(file)
                                elif "wordprocessingml" in file.type:
                                    text = extract_word_text(file)
                                else:
                                    st.warning(f"Unsupported file type for {file.name}. Skipping.")
                                    continue

                                if text.strip():
                                    content += f"\n\n--- FILE: {file.name} ---\n{text}"
                                    files_processed.append(f"📄 {file.name}")
                                    st.toast(f"✅ Loaded: {file.name}", icon="📄")
                                else:
                                    st.warning(f"No usable text extracted from {file.name}.")
                            else:
                                st.info(f"File '{file.name}' was already processed.")

                    if urls_input.strip():
                        urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
                        for url in urls:
                            if url not in existing_processed_names:
                                text = extract_url_text(url)
                                if text.strip():
                                    content += f"\n\n--- URL: {url} ---\n{text}"
                                    files_processed.append(f"🌐 {url}")
                                    st.toast(f"✅ Loaded: {url}", icon="🌐")
                                else:
                                    st.warning(f"No content extracted or invalid URL: {url}")
                            else:
                                st.info(f"URL '{url}' was already processed.")

                st.session_state.all_content += content
                st.session_state.processed_files.extend(files_processed)

                if st.session_state.all_content:
                    st.success(f"Content processing complete! Total unique sources: {len(st.session_state.processed_files)}")
                else:
                    st.warning("No content was added after processing. Please check inputs.")

        if st.session_state.processed_files:
            st.markdown(f'<div class="status-info">📁 Currently loaded: {len(st.session_state.processed_files)} sources</div>', unsafe_allow_html=True)
            with st.expander("View loaded sources"):
                for source in st.session_state.processed_files:
                    st.write(f"- {source}")
        else:
            st.info("No content loaded yet. Upload files or enter URLs above.")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.all_content:
            st.markdown("""
            <div class="content-section">
                <div class="section-title"> Now, Ask Questions... </div>
            """, unsafe_allow_html=True)

            with st.form("question_form"):
                col_q1, col_q2 = st.columns(2)
                with col_q1:
                    if st.form_submit_button("💬 Summarize content", help="Ask Gemini to summarize all loaded content."):
                        st.session_state.quick_question = "Can you provside a summary of the loaded content?"
                with col_q2:
                    if st.form_submit_button("🔍 Key findings", help="Ask Gemini for the key findings or conclusions from the content."):
                        st.session_state.quick_question = "What are the key findings or conclusions from the loaded content?"

                question = st.text_input(
                    "Your question:",
                    value=st.session_state.quick_question,
                    placeholder="What would you like to know about the content?",
                    key="user_question_input"
                )
                
                submit_button = st.form_submit_button("🤖 Get Answer", type="primary", use_container_width=True)

                if submit_button:
                    if question.strip():
                        with st.spinner("Generating response... Just relax for few seconds we will make it for you....!!!"):
                            response = ask_gemini(st.session_state.all_content, question, gemini_api_key)

                        st.markdown(f"""
                        <div class="response-box">
                            <h4>Response from your Files/Links:</h4>
                            <div class="response-content">{response}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.session_state.quick_question = ""
                    else:
                        st.error("Please enter a question before clicking 'Get Answer'.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.all_content or st.session_state.processed_files:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All Loaded Data", help="Removes all uploaded files and processed URLs from the session."):
            st.session_state.all_content = ""
            st.session_state.processed_files = []
            st.success("All data cleared! You can now upload new content.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()