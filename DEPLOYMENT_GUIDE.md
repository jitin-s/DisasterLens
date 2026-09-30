# DisasterLens: Cloud Deployment Guide

This guide explains how to deploy DisasterLens to **Vercel**, **Streamlit Community Cloud**, or **Docker/Render**.

----

### Option 1: Deploy on Vercel (Step-by-Step)

The repository comes pre-configured with [`vercel.json`](file:///D:/DisasterLens/vercel.json) and [`api/index.py`](file:///D:/DisasterLens/api/index.py).

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add DisasterLens national portal, bilingual support, and AI chatbot"
   git push origin main
   ```
2. **Go to Vercel**:
   - Log in to [vercel.com](https://vercel.com).
   - Click **"Add New..."** &rarr; **"Project"**.
   - Import your `DisasterLens` GitHub repository.
3. **Configure Settings**:
   - Framework Preset: **Other**.
   - Root Directory: `./` (leave default).
   - Click **Deploy**.
4. Vercel will build the project using `@vercel/python` according to `vercel.json`.

> [!NOTE]
> **Vercel & Streamlit Architecture Notice**:
> Streamlit is a stateful Python application that relies on active WebSockets (`_stcore/stream`) for live interactive maps and AI chats. Serverless platforms like Vercel have a strict 10–15 second timeout per function call. For the ultimate interactive production experience with zero timeouts, the **Streamlit Community Cloud** (Option 2 below) is officially recommended by Streamlit.

---

## Option 2: Deploy on Streamlit Community Cloud (Recommended & 100% Free)

Streamlit Community Cloud is the official, 100% free hosting platform for Streamlit apps. It provides persistent Python kernels, live WebSockets, and zero timeout interruptions.

### Steps (Takes 60 Seconds):
1. **Push your code to GitHub**:
   Ensure your repo contains `app/main.py` and `requirements.txt`.
2. **Open Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
3. **Click "New app"**:
   - **Repository**: Choose your `DisasterLens` repo.
   - **Branch**: `main`.
   - **Main file path**: `app/main.py`.
   - **App URL**: Choose a custom subdomain (e.g., `disasterlens.streamlit.app`).
4. **Click "Deploy!"**:
   Streamlit Cloud installs dependencies from `requirements.txt` and launches the portal. Your app is live with a public HTTPS URL!

---

## Option 3: Deploy with Docker (Render, Railway, or Google Cloud Run)

The repository includes a production [`Dockerfile`](file:///D:/DisasterLens/Dockerfile).

### On Render.com (Free Tier):
1. Go to [render.com](https://render.com) and create a **New Web Service**.
2. Connect your GitHub repository.
3. Select **Docker** as the runtime environment.
4. Set Port to `8501`.
5. Click **Create Web Service**.

### Locally via Docker:
```bash
docker build -t disasterlens:latest .
docker run -p 8501:8501 disasterlens:latest
```
Visit `http://localhost:8501` in your browser.
