import streamlit as st
from google import genai
import re

# 1. ИНТЕРФЕЙС ПЕН ТҮСТЕРДІ БАПТАУ (Ақ түстерді жою)
st.set_page_config(page_title="Аманат: Тас Қамал", layout="wide")

st.markdown("""
    <style>
    /* Негізгі фон - Тас қабырға стилі */
    .stApp { 
        background-color: #2b2b2b !important;
        background-image: url("https://www.transparenttextures.com/patterns/dark-brick-wall.png") !important;
    }

    /* Хабарламалар - Ескі пергамент (ақ емес, сарғайған қоңыр) */
    [data-testid="stChatMessage"] {
        background-color: #d2b48c !important; 
        border: 2px solid #5d4037 !important;
        border-radius: 10px !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }

    /* Мәтін түсі - Қара қоңыр сия */
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
        color: #2b1d0e !important;
        font-family: 'Georgia', serif !important;
        font-weight: bold !important;
    }

    /* Төменгі хабарлама жазатын жер (Input) - Күңгірт түс */
    .stChatInputContainer {
        background-color: #1e1e1e !important;
        border: 1px solid #5d4037 !important;
        border-radius: 15px !important;
        padding: 5px !important;
    }
    
    .stChatInputContainer textarea {
        background-color: #2d2d2d !important;
        color: #d2b48c !important; /* Жазу түсі пергаментке ұқсайды */
    }

    /* Sidebar (Сол жақ мәзір) */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 3px solid #5d4037 !important;
    }

    /* Тақырып - Алтын түсті */
    h1 {
        color: #ffd700 !important;
        text-shadow: 2px 2px 4px #000;
        text-align: center;
    }

    /* Метрикалар мен батырмалар */
    [data-testid="stMetricValue"] { color: #ff4b4b !important; }
    .stButton>button {
        background-color: #3e2723 !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API ЖӘНЕ ЛОГИКА
API_KEYS = [
    "AIzaSyAaM65YEUXytn151oNlHLSCFCdYHICOgy8",
    "AIzaSyArLaqy6r3rJw3rcTpLrWgnA2PFN5cTgxI"
]

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

def get_client():
    return genai.Client(api_key=API_KEYS[st.session_state.key_index])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "hp" not in st.session_state:
    st.session_state.hp = 100

if "chat" not in st.session_state:
    client = get_client()
    st.session_state.chat = client.chats.create(model="gemini-2.0-flash")
    persona = "Сен қатал Елессің. Қамал зынданы. Жауап соңында [HP: -10] жаз."
    try:
        resp = st.session_state.chat.send_message(persona + " Ойынды баста.")
        st.session_state.messages.append({"role": "assistant", "content": resp.text})
    except: pass

# 3. ЭКРАН
st.title("🏰 АМАНАТ: ТАС ҚАМАЛ")

with st.sidebar:
    st.header("👤 СТАТУС")
    st.metric("❤️ ӨМІР", f"{st.session_state.hp}%")
    
    st.markdown("---")
    if st.button("🔑 КІЛТТІ АУЫСТЫРУ"):
        if st.session_state.key_index < len(API_KEYS) - 1:
            st.session_state.key_index += 1
            st.success("Кілт ауыстырылды!")
            st.session_state.chat = get_client().chats.create(model="gemini-2.0-flash")
        else:
            st.error("Басқа кілт жоқ!")

    if st.button("🔄 ҚАЙТА БАСТАУ"):
        st.session_state.clear()
        st.rerun()

# Чатты көрсету
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Хабарлама жіберу
if prompt := st.chat_input("Әрекетіңіз..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        response = st.session_state.chat.send_message(prompt)
        text = response.text
        hp_match = re.search(r"\[HP:\s*([+-]?\d+)\]", text)
        if hp_match:
            st.session_state.hp += int(hp_match.group(1))
        st.session_state.messages.append({"role": "assistant", "content": text})
        st.rerun()
    except:
        st.warning("⌛ Лимит. 20 секунд күте тұрыңыз немесе кілтті ауыстырыңыз.")

if st.session_state.hp <= 0:
    st.error("💀 СЕН ӨЛДІҢ!")
    st.stop()