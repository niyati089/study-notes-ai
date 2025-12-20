# utils/ui_styles.py
"""
Whimsical Apple-inspired UI themes for Streamlit
Combines Apple's clean aesthetics with playful, twee elements
"""

def apply_whimsical_theme():
    """
    Apply custom CSS for a whimsical, Apple-inspired aesthetic
    Features: Soft gradients, rounded corners, glassmorphism, playful animations
    """
    return """
    <style>
    /* Import Apple-style fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Shrikhand&family=Fredoka:wght@300;400;500;600&display=swap');
    
    /* Root variables - Apple-inspired color palette */
    :root {
        --apple-blue: #007AFF;
        --apple-pink: #FF2D55;
        --apple-purple: #AF52DE;
        --apple-teal: #5AC8FA;
        --apple-green: #34C759;
        --apple-yellow: #FFCC00;
        --apple-orange: #FF9500;
        --apple-red: #FF3B30;
        --cream: #FFF8F0;
        --sage: #B8C5B0;
        --lavender: #E6E6FA;
        --peach: #FFE5D9;
        --mint: #D4F1F4;
    }
    
    /* Main app background - soft gradient */
    .stApp {
        background: linear-gradient(135deg, 
            var(--cream) 0%, 
            var(--mint) 50%, 
            var(--lavender) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Animated floating elements in background */
    .stApp::before {
        content: '🍎✨🌸🦋🌈☁️🌟🍃';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        font-size: 3rem;
        opacity: 0.05;
        letter-spacing: 8rem;
        line-height: 8rem;
        pointer-events: none;
        z-index: 0;
        animation: float 60s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
        100% { transform: translateY(0) rotate(360deg); }
    }
    
    /* Main title styling */
    h1 {
        font-family: 'Fredoka', 'Inter', sans-serif !important;
        background: linear-gradient(135deg, var(--apple-pink), var(--apple-purple), var(--apple-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        text-align: center;
        padding: 1.5rem 0;
        font-size: 3rem !important;
        text-shadow: 0 2px 20px rgba(255, 45, 85, 0.2);
        animation: titlePulse 3s ease-in-out infinite;
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Subheaders */
    h2, h3 {
        font-family: 'Fredoka', 'Inter', sans-serif !important;
        color: var(--apple-purple) !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar styling - Frosted glass effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Sidebar header with emoji */
    [data-testid="stSidebar"] h1::before {
        content: "🎨 ";
    }
    
    /* Cards and containers - Apple-style elevated cards */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 122, 255, 0.15),
                    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
    }
    
    /* Expanders - Playful accordion style */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--peach), var(--mint)) !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 600 !important;
        color: var(--apple-purple) !important;
        padding: 1rem 1.5rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, var(--apple-pink), var(--apple-teal)) !important;
        color: white !important;
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(255, 45, 85, 0.2);
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 0 0 15px 15px;
        padding: 1.5rem;
        border: 1px solid rgba(175, 82, 222, 0.1);
        border-top: none;
    }
    
    /* Buttons - Apple-style with gradients */
    .stButton > button {
        background: linear-gradient(135deg, var(--apple-blue), var(--apple-teal)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3),
                    0 0 0 1px rgba(255, 255, 255, 0.3) inset !important;
        text-transform: none !important;
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--apple-purple), var(--apple-pink)) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(175, 82, 222, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Special button variants */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, var(--sage), var(--mint)) !important;
        color: var(--apple-purple) !important;
    }
    
    /* Input fields - Soft and rounded */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid rgba(175, 82, 222, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--apple-blue) !important;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1),
                    0 4px 15px rgba(0, 122, 255, 0.2) !important;
        transform: scale(1.01);
    }
    
    /* File uploader - Whimsical drop zone */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.9), 
            rgba(212, 241, 244, 0.6)) !important;
        border: 3px dashed var(--apple-teal) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--apple-purple) !important;
        background: linear-gradient(135deg, 
            rgba(255, 229, 217, 0.8), 
            rgba(230, 230, 250, 0.6)) !important;
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(175, 82, 222, 0.2);
    }
    
    [data-testid="stFileUploader"]::before {
        content: " Drop your PDFs here! ";
        display: block;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--apple-purple);
        margin-bottom: 1rem;
        font-family: 'Fredoka', sans-serif;
    }
    
    /* Sliders - Colorful and smooth */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, 
            var(--apple-pink), 
            var(--apple-orange), 
            var(--apple-yellow)) !important;
        border-radius: 10px !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: white !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        border: 3px solid var(--apple-purple) !important;
    }
    
    /* Success/Info/Warning messages - Playful alerts */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 15px !important;
        border-left: 5px solid !important;
        padding: 1rem 1.5rem !important;
        backdrop-filter: blur(10px);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateX(-20px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }
    
    .stSuccess {
        background: rgba(52, 199, 89, 0.1) !important;
        border-left-color: var(--apple-green) !important;
    }
    
    .stInfo {
        background: rgba(0, 122, 255, 0.1) !important;
        border-left-color: var(--apple-blue) !important;
    }
    
    .stWarning {
        background: rgba(255, 204, 0, 0.1) !important;
        border-left-color: var(--apple-yellow) !important;
    }
    
    /* Add emoji bullets to markdown lists */
    .stMarkdown li::before {
        content: " ";
        margin-right: 0.5rem;
    }
    
    /* Tabs - Pill style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        padding: 0.75rem 1.5rem !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, var(--peach), var(--mint)) !important;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--apple-pink), var(--apple-purple)) !important;
        color: white !important;
        border: 2px solid white !important;
        box-shadow: 0 4px 15px rgba(255, 45, 85, 0.3);
    }
    
    /* Scrollbar - Minimal and pretty */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--apple-pink), var(--apple-purple));
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--apple-blue), var(--apple-teal));
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 15px !important;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Spinner - Cute loading animation */
    .stSpinner > div {
        border-top-color: var(--apple-pink) !important;
        border-right-color: var(--apple-purple) !important;
        border-bottom-color: var(--apple-blue) !important;
        border-left-color: var(--apple-teal) !important;
    }
    
    /* Code blocks - Developer friendly but pretty */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid rgba(175, 82, 222, 0.2) !important;
        background: rgba(255, 248, 240, 0.9) !important;
    }
    
    /* Metric cards - Dashboard style */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.9), 
            rgba(230, 230, 250, 0.5)) !important;
        padding: 1rem !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--apple-green), var(--apple-teal)) !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, var(--apple-blue), var(--apple-purple)) !important;
    }
    
    /* Add decorative elements to columns */
    [data-testid="column"]:nth-child(1)::before {
        content: "";
        position: absolute;
        top: -10px;
        left: -10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    [data-testid="column"]:nth-child(2)::before {
        content: "";
        position: absolute;
        top: -10px;
        left: -10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    [data-testid="column"]:nth-child(3)::before {
        content: "📝";
        position: absolute;
        top: -10px;
        left: -10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    /* Footer styling */
    footer {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(175, 82, 222, 0.1);
        padding: 2rem !important;
        margin-top: 3rem;
        border-radius: 20px 20px 0 0;
    }
    
    /* Subtle animations on page load */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .element-container {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Dark mode support (if enabled) */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, 
                #1a1a2e 0%, 
                #16213e 50%, 
                #0f3460 100%);
        }
        
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            background: rgba(30, 30, 46, 0.85);
            border: 1px solid rgba(175, 82, 222, 0.3);
        }
    }
    </style>
    """


def get_decorative_emoji(section):
    """
    Returns appropriate emoji for different sections
    """
    emojis = {
        "pdf": "",
        "chat": "",
        "notes": "",
        "flashcards": "",
        "summary": "",
        "upload": "",
        "settings": "",
        "success": "",
        "loading": "",
        "save": "",
        "download": "⬇",
        "generate": "",
        "search": ""
    }
    return emojis.get(section, "")


def create_gradient_text(text, gradient_type="rainbow"):
    """
    Create gradient text HTML
    """
    gradients = {
        "rainbow": "linear-gradient(135deg, #FF2D55, #AF52DE, #007AFF, #5AC8FA)",
        "sunset": "linear-gradient(135deg, #FF9500, #FF3B30, #FF2D55)",
        "ocean": "linear-gradient(135deg, #007AFF, #5AC8FA, #34C759)",
        "purple": "linear-gradient(135deg, #AF52DE, #FF2D55)",
        "mint": "linear-gradient(135deg, #34C759, #5AC8FA)"
    }
    
    gradient = gradients.get(gradient_type, gradients["rainbow"])
    
    return f"""
    <span style="
        background: {gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.2em;
    ">{text}</span>
    """


def create_card_container(content, title=None, icon=None):
    """
    Create a beautiful card container for content
    """
    title_html = f"<h3 style='margin-top: 0;'>{icon} {title}</h3>" if title and icon else ""
    
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    ">
        {title_html}
        {content}
    </div>
    """


def create_badge(text, color="blue"):
    """
    Create a small badge/pill
    """
    colors = {
        "blue": "#007AFF",
        "pink": "#FF2D55",
        "purple": "#AF52DE",
        "green": "#34C759",
        "orange": "#FF9500"
    }
    
    bg_color = colors.get(color, colors["blue"])
    
    return f"""
    <span style="
        background: {bg_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    ">{text}</span>
    """