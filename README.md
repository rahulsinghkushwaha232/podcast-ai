# Podcast Recommendation App 🎧

A Flask-powered podcast recommender with a clean HTML frontend.

## Features
- Query-based podcast recommendations via the iTunes Search API
- CORS-enabled backend for local frontend development
- Simple HTML/CSS/JS frontend
- Ready for deployment

## Run Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `frontend/index.html` in your browser, or open
http://localhost:5000/app after starting the backend. The `/app` route serves
the frontend directly from Flask, so a second web server is not required.

For an optional separate frontend server:

```powershell
# Terminal 1 - backend
cd C:\Users\ASUS\OneDrive\Attachments\ChatBot\backend
.\venv\Scripts\python.exe app.py

# Terminal 2 - frontend
cd C:\Users\ASUS\OneDrive\Attachments\ChatBot\frontend
python -m http.server 8000
```

Open http://localhost:8000/index.html. The frontend calls the backend at
http://localhost:5000/recommend. Alternatively, open http://localhost:5000/app and use the `Run PodcastAI`
task. The task starts only the integrated Flask app, avoiding an unnecessary
second server and port.

For Windows PowerShell, use:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## 👥 Contributors & Authors

- **Rahul Singh Kushwaha** - [@rahulsinghkushwaha232](https://github.com/rahulsinghkushwaha232) (Lead Developer)
- **PodcastAI Team**

