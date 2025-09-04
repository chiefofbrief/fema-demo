import streamlit as st
import anthropic
import os
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(
    page_title="FEMA Public Assistance Demo",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f4e79;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f4e79;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem !important;
        color: #2c5aa0;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .demo-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .chat-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Increase base font size for better readability */
    .stMarkdown, .stText, p, div {
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
    }
    
    /* Make chat messages larger */
    .stChatMessage {
        font-size: 1.2rem !important;
    }
    
    /* Style for transition questions */
    .transition-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #ffd700;
    }
    
    /* Style for section openings */
    .opening-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Better bullet points */
    .custom-bullets li {
        font-size: 1.2rem !important;
        margin-bottom: 0.8rem !important;
        line-height: 1.6 !important;
    }
    
    /* Larger text input area */
    .stTextInput > div > div > input {
        font-size: 1.2rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea > div > div > textarea {
        font-size: 1.2rem !important;
        padding: 1rem !important;
        min-height: 150px !important;
    }
    
    /* Make chat input larger */
    .stChatInput > div > div > div > div {
        min-height: 60px !important;
        font-size: 1.2rem !important;
        padding: 1rem !important;
    }
    
    /* Smaller, less prominent photo upload */
    .stFileUploader {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px dashed #ccc;
    }
    
    .stFileUploader > div {
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Anthropic client
@st.cache_resource
def init_anthropic():
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")
            st.stop()
        
        client = anthropic.Anthropic(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing Anthropic client: {e}")
        st.stop()

client = init_anthropic()

# Load prompt from file
@st.cache_data
def load_prompt():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Prompt file not found. Please create prompt.txt with your workflow instructions."

# Load documents
def load_document(doc_name):
    try:
        with open(f"documents/{doc_name}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Document {doc_name} not found"

# Initialize session state
if 'demo_started' not in st.session_state:
    st.session_state.demo_started = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title and subtitle (always show)
st.markdown('<h1 class="main-header">FEMA Public Assistance Demo</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #666; margin-bottom: 2rem;">Severe Thunderstorm Emma (DR-7890) - Emergency Declaration</h3>', unsafe_allow_html=True)

# Main content
if not st.session_state.demo_started:
    # INTRO SCREEN
    with st.container():
        st.markdown('<div class="demo-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📋 Demo Overview</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        This demo illustrates how foundation models can accelerate disaster recovery grant delivery to state and local governments. 
        
        Typically, following a federal disaster declaration, local governments assess damages, wait for FEMA personnel to arrive, 
        conduct multiple meetings with FEMA, and rely on Program Managers to develop grant applications and evaluate eligibility. 
        **This process normally takes months, but as you'll see, it can be completed much faster with AI assistance.**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Ready to Begin Demo", type="primary", use_container_width=True):
            st.session_state.demo_started = True
            st.rerun()

else:
    # CHAT SCREEN
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">💬 FEMA PA Specialist Chat</h2>', unsafe_allow_html=True)
        
        # Initialize first message from prompt if needed
        if not st.session_state.messages:
            # Get the initial message from Claude using the prompt
            try:
                system_prompt = load_prompt()
                docs_context = f"""
                Reference Documents:
                Damage Inventory Guide: {load_document('damage_inventory_guide')}
                General Eligibility: {load_document('general_eligibility_considerations')}
                Emergency Work Eligibility: {load_document('emergency_work_eligibility')}
                Project Formulation Guide: {load_document('project_formulation_guide')}
                Documentation Requirements: {load_document('documentation_requirements')}
                """
                
                full_prompt = system_prompt + "\n\n" + docs_context
                
                # Request the introduction message
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    temperature=0.7,
                    system=full_prompt,
                    messages=[{"role": "user", "content": "Please provide the introduction message to start the FEMA Public Assistance demo."}]
                )
                
                intro_response = response.content[0].text
                st.session_state.messages.append({"role": "assistant", "content": intro_response})
            except Exception as e:
                # Fallback to basic intro if prompt fails
                intro = "Hi! I'm here to help you navigate FEMA Public Assistance grants. Let me know about your storm damage and we'll get started."
                st.session_state.messages.append({"role": "assistant", "content": intro})
        
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
        
        # Add sample text section - show after first assistant message
        if len(st.session_state.messages) == 1:
            with st.expander("📝 Need help getting started? Click here for sample text you can copy and use"):
                sample_text = """We had trees down all over - big old oaks that blocked several roads and took out some lamp posts on Elm Street. The vendor booths at Memorial Park got completely destroyed.

We prepared by putting plywood over windows at city hall and setting up sandbags around the building since that area always floods. Police did extra patrols to help with evacuations.

During the storm we sheltered about 300 people at Washington Elementary and Jefferson High for a couple days until we could clear roads and restore power.

Now we need to clear debris from about half the township - tree limbs plus some appliances residents put out after basement flooding. We need to replace the lamp posts, rebuild those vendor booths, fix broken windows at city hall, and repair a section of Oak Street where a big tree tore up the asphalt."""
                
                st.text_area("Sample damage description:", value=sample_text, height=120, key="sample_text", help="Select all text (Ctrl+A) and copy (Ctrl+C)")
                st.info("💡 Select all text above (Ctrl+A), copy (Ctrl+C), then paste into the chat input below to see how the demo works!")
        
        # Image upload section - only show initially
        if len(st.session_state.messages) <= 1:
            st.markdown("---")
            
            # More compact photo upload section
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown('<h4 style="color: #2c5aa0; margin-bottom: 1rem;">📸 Upload Photos (Optional)</h4>', unsafe_allow_html=True)
                uploaded_images = st.file_uploader(
                    "Upload damage photos", 
                    type=['png', 'jpg', 'jpeg'], 
                    accept_multiple_files=True,
                    help="Add photos to help with damage assessment",
                    key="photo_uploader",
                    label_visibility="collapsed"
                )
            
            # Process uploaded images
            if uploaded_images:
                with col2:
                    for uploaded_file in uploaded_images:
                        try:
                            image = Image.open(uploaded_file)
                            st.image(image, caption=uploaded_file.name, width=200)
                        except Exception as e:
                            st.error(f"Error processing image {uploaded_file.name}: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input - moved outside the container
    # Dynamic placeholder text based on conversation stage
    if len(st.session_state.messages) <= 1:
        placeholder_text = "Describe the storm damage and your response..."
    else:
        placeholder_text = "Please answer the questions above..."
        
    if prompt := st.chat_input(placeholder_text, key="main_chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your response..."):
                try:
                    system_prompt = load_prompt()
                    docs_context = f"""
                    Reference Documents:
                    Damage Inventory Guide: {load_document('damage_inventory_guide')}
                    General Eligibility: {load_document('general_eligibility_considerations')}
                    Emergency Work Eligibility: {load_document('emergency_work_eligibility')}
                    Project Formulation Guide: {load_document('project_formulation_guide')}
                    Documentation Requirements: {load_document('documentation_requirements')}
                    """
                    
                    full_prompt = system_prompt + "\n\n" + docs_context
                    
                    claude_messages = []
                    for msg in st.session_state.messages:
                        claude_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=8000,
                        temperature=0.7,
                        system=full_prompt,
                        messages=claude_messages
                    )
                    
                    ai_response = response.content[0].text
                    st.markdown(ai_response, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.rerun()  # Refresh to update the display
    
    # Reset button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Reset Demo", use_container_width=True):
            st.session_state.demo_started = False
            st.session_state.messages = []
            st.rerun()
