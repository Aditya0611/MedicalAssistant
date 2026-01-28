import hashlib
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import pandas as pd
import random
import re
import os
import tempfile
from difflib import get_close_matches
import streamlit as st
import kagglehub
import database
import calendar_utils
import symptom_analyzer
import voice_utils
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64

@st.cache_resource
def load_doctor_data():
    path = kagglehub.dataset_download("niksaurabh/doctors-speciality")
    csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]
    if csv_files:
        file_path = os.path.join(path, csv_files[0])
        df = pd.read_csv(file_path)
        return df.groupby('speciality')['Doctor\'s Name'].apply(list).to_dict()
    return {}

doctors_by_specialty = load_doctor_data()

def send_email(to_email, subject, body):
    sender_email = "adityaraj6112025@gmail.com"
    password = "kjowmfcicgzkqnti"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def validate_mobile(mobile):
    # Check if exactly 10 digits and only digits
    return bool(re.match(r'^\d{10}$', mobile))

def validate_name(name):
    if not name or len(name.strip()) < 2:
        return False
    if name[0].isdigit():
        return False
    return True

def parse_date(date_str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError: continue
    return None

def parse_time(time_str):
    if not time_str: return None
    t = time_str.lower().replace(".", "").replace(" ","").strip()
    formats = ["%I:%M%p", "%I%p", "%H:%M", "%I.%M%p"]
    for fmt in formats:
        try:
            return datetime.strptime(t, fmt).strftime("%I:%M %p")
        except ValueError: continue
    if "noon" in t: return "12:00 PM"
    if "midnight" in t: return "12:00 AM"
    return None

def is_past_date(date_str):
    return date_str < datetime.today().strftime("%Y-%m-%d")

def is_past_time(date_str, time_str):
    if date_str == datetime.today().strftime("%Y-%m-%d"):
        return time_str < datetime.now().strftime("%I:%M %p")
    return False

def is_time_slot_available(date_str, time_str, doctor):
    return database.check_availability(date_str, time_str, doctor)

def speak_text(text):
    if not text: return
    try:
        # Normalize text for speech (e.g. remove numbering for cleaner speech)
        clean_text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        tts = gTTS(text=clean_text, lang='en', tld='co.in')
        fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            tts.save(tmp_path)
            with open(tmp_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                # Use a unique key for the audio element to force re-render if needed
                md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
        finally:
            if os.path.exists(tmp_path): os.remove(tmp_path)
    except Exception as e: print(f"TTS Error: {e}")

def normalize_input(text):
    if not text: return ""
    text = text.lower().strip()
    word_to_digit = {"one": "1", "book": "1", "two": "2", "reschedule": "2", "three": "3", "cancel": "3", "four": "4", "medical": "4", "five": "5"}
    for word, digit in word_to_digit.items():
        if word in text: return digit
    digits = re.findall(r'\d+', text)
    return digits[0] if digits else text

def get_next_missing_field():
    required = ["name", "email", "mobile", "age", "gender", "symptoms", "selected_doctor", "appointment_date", "appointment_time"]
    details = st.session_state["appointment_details"]
    for field in required:
        if not details.get(field): return field
    return "confirm_appointment"

def is_complex_input(text, current_step=None):
    if not text: return False
    if current_step in ["symptoms", "appointment_time", "appointment_date"]:
        if not re.match(r'^\d{1,2}$', text.strip()): return True
    words = text.strip().split()
    if len(words) > 4: return True
    keywords = ["and", "have", "with", "my", "is", "am", "at", "on"]
    if any(k in text.lower() for k in keywords) and len(words) > 2: return True
    return False

def ask_step_question(step):
    questions = {
        "name": "What is your full name?",
        "email": "What is your email address?",
        "mobile": "What is your mobile number? Please speak only digits.",
        "age": "What is your age?",
        "gender": "What is your gender? Male, Female, or Transgender?",
        "symptoms": "Please describe the symptoms you are experiencing.",
        "appointment_date": "On which date would you like to visit?",
        "appointment_time": "At what time would you prefer your appointment?",
        "confirm_appointment": "Do you want to confirm this booking? Say yes or no."
    }
    msg = questions.get(step)
    if msg and (not st.session_state["messages"] or st.session_state["messages"][-1]["content"] != msg):
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.session_state["to_speak"] = msg
        # Remove st.rerun() from here if present to allow immediate rendering

def inject_custom_css():
    css = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet"><style>@keyframes meshGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); transform: scale(1); } 70% { box-shadow: 0 0 0 20px rgba(99, 102, 241, 0); transform: scale(1.05); } 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); transform: scale(1); } }.stApp { background-color: #030712; background-image: radial-gradient(circle at 20% 20%, rgba(79, 70, 229, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%), radial-gradient(circle at 50% 50%, rgba(31, 41, 55, 0.2) 0%, transparent 70%); background-size: 200% 200%; animation: meshGradient 20s ease infinite; background-attachment: fixed; font-family: 'Inter', sans-serif; }.title { font-family: 'Outfit', sans-serif; font-size: clamp(28px, 5vw, 46px); font-weight: 700; background: linear-gradient(135deg, #ffffff 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; padding: 20px 10px 40px; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4)); }.stChatMessage { border-radius: 24px !important; padding: 1.5rem !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; background: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(30px); margin-bottom: 1.5rem !important; }.stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div { color: #ffffff !important; font-family: 'Inter', sans-serif !important; font-size: 1rem !important; line-height: 1.6 !important; }.dashboard-item { background: rgba(31, 41, 55, 0.6); padding: 20px; border-radius: 20px; margin-bottom: 15px; border-left: 5px solid #6366f1; transition: 0.3s; }.dashboard-item:hover { transform: translateY(-2px); background: rgba(31, 41, 55, 0.8); }.assistant-header { color: #a5b4fc !important; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.2rem; letter-spacing: 2px; margin-bottom: 20px; text-transform: uppercase; }.stMicRecorder button { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important; color: white !important; padding: 12px 30px !important; border-radius: 100px !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; font-size: 1rem !important; text-transform: uppercase !important; letter-spacing: 2px !important; transition: 0.4s all cubic-bezier(0.175, 0.885, 0.32, 1.275) !important; cursor: pointer !important; width: 100% !important; } .stMicRecorder button [data-recording="true"] { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important; animation: pulse 1.5s infinite !important; }@media (max-width: 900px) { [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; } }@media (max-width: 768px) { .stChatMessage { padding: 1rem !important; border-radius: 16px !important; } .dashboard-item { padding: 15px !important; } }div[data-testid="stChatInput"] { background-color: rgba(255, 255, 255, 0.95) !important; border: 2px solid #6366f1 !important; border-radius: 20px !important; }#MainMenu, header, footer {visibility: hidden;}</style>"""
    st.markdown(css, unsafe_allow_html=True)

def handle_chat():
    if "step" not in st.session_state: st.session_state["step"] = None
    if "messages" not in st.session_state: st.session_state["messages"] = []
    if "appointment_details" not in st.session_state: st.session_state["appointment_details"] = {}
    if "audio_key_index" not in st.session_state: st.session_state["audio_key_index"] = 0

    # 0. DATABASE CHECK
    is_connected, db_error = database.test_connection()
    if not is_connected:
        st.error(f"🚨 Connection Error: {db_error}")
        st.stop()

    # Create Main Columns (Left for Chat, Right for Dashboard)
    col_chat, col_dash = st.columns([1.8, 1])

    # 1. RIGHT SECTION - PATIENT PROFILE
    with col_dash:
        st.markdown('<div style="text-align: center; padding: 20px;"><h2 style="color: #6366f1; font-family: \'Outfit\', sans-serif;">🏥 Patient Dashboard</h2></div>', unsafe_allow_html=True)
        det = st.session_state["appointment_details"]
        
        # Display Cards
        st.markdown(f'''
            <div class="dashboard-item" style="color: white; padding: 15px;">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Patient Name</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #ffffff;">{det.get("name", "---")}</div>
            </div>
            <div class="dashboard-item" style="color: white; padding: 15px;">
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Patient Email</div>
                <div style="font-size: 0.95rem; font-weight: 500; color: #ffffff; word-break: break-all;">{det.get("email", "---")}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Grid for cards
        sc1, sc2 = st.columns(2)
        with sc1: st.markdown(f'<div class="dashboard-item" style="padding: 12px; color: white;"><div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Age</div><div style="color: white;">{det.get("age", "--")}</div></div>', unsafe_allow_html=True)
        with sc2: st.markdown(f'<div class="dashboard-item" style="padding: 12px; color: white;"><div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Gender</div><div style="color: white;">{det.get("gender", "--")}</div></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="dashboard-item" style="border-left-color: #818cf8; color: white;"><div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Medical Specialist</div><div style="color: #a5b4fc; font-weight: 600;">{det.get("selected_doctor", "Awaiting Analysis...")}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="dashboard-item" style="color: white;"><div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Appointment</div><div style="color: white;">📅 {det.get("appointment_date", "Not Set")}</div><div style="color: white;">🕒 {det.get("appointment_time", "Not Set")}</div></div>', unsafe_allow_html=True)
        
        if st.button("Reset Session", use_container_width=True):
            st.session_state["messages"] = []; st.session_state["appointment_details"] = {}; st.session_state["step"] = None; st.rerun()

    with col_chat:
        # 2. CHAT HISTORY
        for m in st.session_state["messages"]:
            with st.chat_message(m["role"]): st.write(m["content"])

        # 3. INITIAL GREETING (If app just started)
        if st.session_state["step"] is None and not st.session_state["messages"]:
            welcome_msg = "Welcome! I'm your Medical Assistant. How can I help you today?"
            options_msg = "1. Book Appointment\n2. Reschedule\n3. Cancel\n4. Medical Info\n5. Exit"
            st.session_state["messages"].append({"role": "assistant", "content": welcome_msg})
            st.session_state["messages"].append({"role": "assistant", "content": options_msg})
            st.session_state["step"] = "options"
            st.session_state["to_speak"] = welcome_msg + ". " + options_msg
            st.rerun()

        # 4. VOICE COMPONENT (ALWAYS ABOVE CHAT INPUT)
        with st.container():
            st.markdown("""
                <div style="background: rgba(31, 41, 55, 0.3); padding: 15px; border-radius: 20px; border: 1px solid rgba(99, 102, 241, 0.2); margin-top: 10px; margin-bottom: 5px;">
                    <div style="color: #a5b4fc; font-size: 0.85rem; font-weight: 600; text-align: center; margin-bottom: 8px;">🎙️ VOICE COMMANDS</div>
                    <div style="color: #94a3b8; font-size: 0.75rem; text-align: center; line-height: 1.4;">
                        Click <b>Record</b>, speak clearly, and click <b>Stop</b> to send.<br>
                        "I want to book", "My name is...", "I have a headache"
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            audio = mic_recorder(
                start_prompt="🔴 Start Recording", 
                stop_prompt="✅ Stop & Process", 
                key=f"rec_{st.session_state['audio_key_index']}",
                use_container_width=True
            )
            
            if audio:
                curr_aid = hashlib.md5(audio['bytes']).hexdigest()
                if st.session_state.get("last_audio_id") != curr_aid:
                    with st.spinner("Analyzing your voice..."):
                        txt = voice_utils.transcribe_audio(audio['bytes'])
                        if txt:
                            st.session_state["pending_input"] = txt
                            st.session_state["last_audio_id"] = curr_aid
                            st.session_state["audio_key_index"] += 1
                            st.rerun()

        # 5. INPUT HANDLING (Inside col_chat)
        user_input = st.chat_input("Type or say anything...")
    if st.session_state.get("pending_input"):
        user_input = st.session_state.pop("pending_input")

    if user_input:
        step = st.session_state["step"]
        # --- SMART AI EXTRACTION ---
        if step not in [None, "options", "medical_info"] and is_complex_input(user_input, step):
             with st.spinner("AI is understanding..."):
                extracted = symptom_analyzer.extract_entities(user_input)
                if extracted:
                    for k, v in extracted.items():
                        if v and not st.session_state["appointment_details"].get(k):
                            if k == "email": v = str(v).lower().replace(" ", "").strip()
                            st.session_state["appointment_details"][k] = v

        # --- STEP HANDLER ---
        if step == "options":
            n = normalize_input(user_input)
            if n == "1": st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
            elif n == "2": st.session_state["step"] = "reschedule_email"; ask_step_question("email"); st.rerun()
            elif n == "3": st.session_state["step"] = "cancel_email"; ask_step_question("email"); st.rerun()
            elif n == "4": st.session_state["step"] = "medical_info"; st.session_state["messages"].append({"role": "assistant", "content": "What disease?"}); st.rerun()
            elif n == "5": st.session_state["messages"].append({"role": "assistant", "content": "Goodbye!"}); st.session_state["step"] = None
        elif step == "name":
            if validate_name(user_input):
                st.session_state["appointment_details"]["name"] = user_input
                st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
            else:
                st.error("Invalid name. Name cannot be a single alphabet or start with a numeric value.")
        elif step == "email":
            st.session_state["appointment_details"]["email"] = user_input.lower().replace(" ", "").strip()
            st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
        elif step == "mobile":
            # Strip anything that is not a digit
            c = re.sub(r'\D', '', user_input)
            # If user entered letters, they will be stripped, but we should also check if the raw input had letters
            if any(char.isalpha() for char in user_input):
                st.error("Phone number must be a numeric value.")
            elif validate_mobile(c): 
                st.session_state["appointment_details"]["mobile"] = c
                st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
            else: 
                st.error("Invalid mobile number. Must be 10 digits.")
        elif step == "age":
            c = re.sub(r'\D', '', user_input)
            if c.isdigit() and int(c) > 0: 
                st.session_state["appointment_details"]["age"] = c
                st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
            else:
                st.error("Age must be a numeric value greater than 0.")
        elif step == "gender":
            g = user_input.lower()
            res = "Male" if "mal" in g or "mail" in g else "Female" if "fem" in g else "Transgender" if "trans" in g else None
            if res: st.session_state["appointment_details"]["gender"] = res; st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
        elif step == "symptoms":
            s = user_input; st.session_state["appointment_details"]["symptoms"] = s
            with st.spinner("Analyzing..."):
                ana = symptom_analyzer.analyze_symptom(s)
                spec = ana["specialty"]
                st.session_state["messages"].append({"role": "assistant", "content": f"Recommended Specialty: **{spec}**\n\n{ana['reasoning']}"})
                # Limit to top 5 doctors to prevent data breach/overwhelming list
                docs = doctors_by_specialty.get(spec, ["General Doctor"])[:5]
                st.session_state["appointment_details"]["docs"] = docs
                st.session_state["step"] = "select_doctor"
                sel_msg = "Select doctor:\n" + "\n".join([f"{i+1}. {d}" for i, d in enumerate(docs)])
                st.session_state["messages"].append({"role": "assistant", "content": sel_msg})
                st.session_state["to_speak"] = sel_msg
                st.rerun()
        elif step == "select_doctor":
            docs = st.session_state["appointment_details"].get("docs", [])
            idx = None
            norm = normalize_input(user_input)
            
            # 1. Try numeric matching
            if norm.isdigit():
                i = int(norm) - 1
                if 0 <= i < len(docs):
                    idx = i

            # 2. Try name matching
            if idx is None:
                user_low = user_input.lower()
                for i, d in enumerate(docs):
                    if d.lower() in user_low or user_low in d.lower().replace("dr. ", ""):
                        idx = i
                        break
            
            if idx is not None:
                st.session_state["appointment_details"]["selected_doctor"] = docs[idx]
                st.session_state["step"] = get_next_missing_field()
                ask_step_question(st.session_state["step"])
                st.rerun()
            else:
                st.error(f"Please say the number (1-{len(docs)}) or the doctor's name.")
        elif step == "appointment_date":
            d = parse_date(user_input)
            if not d:
                res = symptom_analyzer.parse_datetime_ai(user_input, f"Today is {datetime.now().strftime('%Y-%m-%d')}")
                if res and res.get("date"): d = res["date"]
            if d and not is_past_date(d): st.session_state["appointment_details"]["appointment_date"] = d; st.session_state["step"] = get_next_missing_field(); ask_step_question(st.session_state["step"]); st.rerun()
        elif step == "appointment_time":
            t = parse_time(user_input)
            if not t:
                res = symptom_analyzer.parse_datetime_ai(user_input, f"Now is {datetime.now().strftime('%I:%M %p')}")
                if res and res.get("time"): t = res["time"]
            if t:
                date = st.session_state["appointment_details"]["appointment_date"]
                if not is_past_time(date, t): st.session_state["appointment_details"]["appointment_time"] = t; st.session_state["step"] = "confirm_appointment"; ask_step_question("confirm_appointment"); st.rerun()
        elif step == "confirm_appointment":
            if normalize_input(user_input) in ["1", "yes", "confirm"]:
                d = st.session_state["appointment_details"]
                res = database.add_appointment(d["email"], d["name"], d["mobile"], int(d["age"]), d["gender"], d["symptoms"], d["selected_doctor"], d["appointment_date"], d["appointment_time"])
                id_str = f"APPT-{res.data[0]['id']}" if res.data and res.data[0].get('id') else "OK"
                
                # --- Send Confirmation Email ---
                email_body = f"""Hello {d['name']},

Your medical appointment has been successfully booked.

Details:
- Appointment ID: {id_str}
- Doctor/Specialist: {d['selected_doctor']}
- Date: {d['appointment_date']}
- Time: {d['appointment_time']}
- Symptoms: {d['symptoms']}

Thank you for using our AI Medical Assistant. Please arrive 15 minutes early.

Best Regards,
Hospital Management Team"""
                send_email(d["email"], f"Appointment Confirmation - {id_str}", email_body)
                
                msg = f"Booked successfully! ID: {id_str}. Confirmation sent to your email."
                st.session_state["messages"].append({"role": "assistant", "content": msg})
                st.session_state["to_speak"] = msg
                st.session_state["step"] = None; st.session_state["appointment_details"] = {}; st.rerun()

def main():
    st.set_page_config(page_title="Medical Assistant", page_icon="🏥", initial_sidebar_state="collapsed", layout="wide")
    inject_custom_css()
    st.markdown('<div class="title">✨ Advanced AI Medical Assistant</div>', unsafe_allow_html=True)
    handle_chat()

    # FINAL AUDIO RENDER (Handles TTS persistence)
    if "to_speak" in st.session_state and st.session_state["to_speak"]:
        text_to_say = st.session_state.pop("to_speak")
        speak_text(text_to_say)

if __name__ == "__main__":
    main()
