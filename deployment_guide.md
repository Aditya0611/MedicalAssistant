# 🌐 AI Medical Assistant - Deployment Guide

This guide explains how to host your AI Medical Assistant on **Streamlit Community Cloud** (Free) so anyone can access it via a URL.

---

## 🏗️ Step 1: Prepare Your Repository
1.  **Upload to GitHub**: Create a new repository on [GitHub](https://github.com) and upload all your project files.
    *   **Files to include**: `python.py`, `database.py`, `calendar_utils.py`, `symptom_analyzer.py`, `voice_utils.py`, `requirements.txt`, and `LICENSE`.
    *   **🚨 IMPORTANT**: Do **NOT** upload your `.env` file. This contains your private keys.
2.  **Verify `requirements.txt`**: Ensure the file exists in your repository. It tells the hosting server which libraries to install.

---

## 🚀 Step 2: Host on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2.  Click **"New app"**.
3.  Select your repository, branch (`main`), and set the Main file path to **`python.py`**.
4.  **Before clicking Deploy**, click on **"Advanced settings..."**.

---

## 🔐 Step 3: Configure Secrets (Essential)
Streamlit Cloud uses a "Secrets" manager instead of a `.env` file. Paste the contents of your local `.env` file into the **Secrets box** in this format:

```toml
GEMINI_API_KEY = "your_key_here"
GROQ_API_KEY = "your_key_here"
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_anon_key"
```

*Click **Save**, then click **Deploy**!*

---

## 📦 Step 4: System Dependencies (Voice Support)
Since your app uses `pydub` and `SpeechRecognition`, Streamlit might need `ffmpeg`.
1.  Create a new file in your GitHub repo named **`packages.txt`** (exactly this name).
2.  Paste this single word inside:
    ```text
    ffmpeg
    ```
3.  Commit and push.

---

## ✅ Deployment Checklist
- [ ] Code is on GitHub.
- [ ] `requirements.txt` is present.
- [ ] `packages.txt` with `ffmpeg` is present.
- [ ] API Secrets are added in Streamlit Cloud Dashboard.
- [ ] Database (Supabase) is reachable.

**Your app will be live at `https://your-app-name.streamlit.app`!** 🏥🚀
