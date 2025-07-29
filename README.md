# ✨ TikTokMaster - Full-Stack TikTok Downloader

TikTokMaster is a full-stack web application that allows users to download TikTok videos, image slideshows, and MP3 audio in all available qualities (up to 8K) without watermarks.

---

## Table of Contents
- [Features](#features)
- [Live Demo](#live-demo)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Local Development Setup](#local-development-setup)
- [Deployment Instructions](#deployment-instructions)
- [Legal Disclaimer](#legal-disclaimer)

---

## ✅ Features

- **High-Quality Video Downloads**: Fetches all available video formats, from 360p to 8K.
- **Image Slideshow Support**: Downloads all images from a TikTok slideshow post.
- **MP3 Audio Extraction**: Provides a direct link to the MP3 audio of any video.
- **No Watermarks**: All downloaded content is clean and watermark-free.
- **Responsive Design**: Mobile-first interface built with Tailwind CSS.
- **Skeleton Loader**: Elegant loading state for a smooth user experience.
- **Ad Integration Ready**: Placeholders for Adsterra Social Bar and Native Banners.

---

## 🚀 Live Demo (Example URLs)

- **Frontend (Vercel)**: `https://your-frontend-app-name.vercel.app`
- **Backend (Render)**: `https://your-backend-service-name.onrender.com`

---

## 🛠️ Tech Stack

- **Backend**:
  - **Language**: Python 3
  - **Framework**: Flask
  - **Core Library**: `yt-dlp`
  - **Server**: Gunicorn
- **Frontend**:
  - **Markup/Styling**: HTML5, Tailwind CSS (via CDN)
  - **Logic**: Vanilla JavaScript (ES6+)
- **Hosting**:
  - **Backend**: Render (or any platform supporting Python/WSGI)
  - **Frontend**: Vercel (or any static hosting provider like Netlify, GitHub Pages)

---

## 🗂️ Folder Structure
TikTokMaster/
│
├── backend/ # Flask API
│ ├── app.py
│ ├── requirements.txt
│ └── Procfile
│
├── frontend/ # Static Site
│ ├── index.html
│ ├── script.js
│ └── styles.css
│
└── README.md


---

## 💻 Local Development Setup

Follow these steps to run the project on your local machine.

### Prerequisites
- Python 3.8+
- `pip` and `venv`

### 1. Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
.\venv\Scripts\activate

# 3. Install the required packages
pip install -r requirements.txt

# 4. Run the Flask development server
# The backend will be available at http://127.0.0.1:8080
flask run --port 8080

