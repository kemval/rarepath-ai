# RarePath AI - Deployment Guide

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
cd rarepath-ai
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Streamlit App
```bash
streamlit run app_streamlit.py
```

The app will open automatically in your browser at: **http://localhost:8501**

---

## ☁️ Deployment Options

### Option 1: Streamlit Cloud (Recommended - FREE)

**Perfect for quick, free deployment!**

#### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `rarepath-ai`
   - Main file: `app_streamlit.py`
   - Click "Deploy"

3. **Add Secrets** (IMPORTANT!)
   - In Streamlit Cloud dashboard, go to your app settings
   - Click "Secrets"
   - Add your API key:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     ```

4. **Share Your App!**
   - You'll get a public URL like: `https://your-app.streamlit.app`
   - Share this link with anyone!

**Benefits:**
- ✅ 100% free
- ✅ No credit card required
- ✅ Automatic HTTPS
- ✅ Easy updates (just push to GitHub)
- ✅ Auto-restart on code changes

---

### Option 2: Google Cloud Run

For more control and scalability.

#### Prerequisites:
- Google Cloud account
- `gcloud` CLI installed

#### Steps:

1. **Authenticate**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```

3. **Deploy**
   ```bash
   gcloud run deploy rarepath-ai \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your-key-here \
     --memory 2Gi \
     --timeout 300
   ```

**Cost:** Free tier includes 2M requests/month. Typical usage: $0-10/month.

---

### Option 3: Other Platforms

The app can be deployed to:
- **Heroku**: Create a `Procfile` with `web: streamlit run app_streamlit.py --server.port=$PORT`
- **AWS EC2/ECS**: Use the included Dockerfile
- **Azure App Service**: Deploy as a container
- **Railway**: Direct deployment from GitHub

---

## 🐛 Troubleshooting

### "Address already in use"
```bash
streamlit run app_streamlit.py --server.port=8502
```

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### API Rate Limits
- The app includes automatic retry logic
- Rate limited to 10 calls/minute to prevent quota exhaustion
- If you hit limits, wait 60 seconds and try again

### Streamlit Cloud Issues
- Make sure `GEMINI_API_KEY` is set in Secrets (not in `.env`)
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` includes all dependencies

---

## 🔄 Updating Your Deployment

### Streamlit Cloud
Just push your changes to GitHub:
```bash
git add .
git commit -m "Update app"
git push origin main
```
Streamlit Cloud will automatically redeploy!

### Cloud Run
Run the deploy command again:
```bash
gcloud run deploy rarepath-ai --source .
```

---

## 🎥 Demo Tips

When recording a demo of your app:

1. **Show the main features**:
   - Enter sample symptoms
   - Display the analysis in progress
   - Show the comprehensive results
   
2. **Highlight technical aspects**:
   - Multi-agent system working together
   - Real-time data from PubMed and ClinicalTrials.gov
   - Session management
   - Professional medical disclaimer

3. **Mention the deployment**:
   - "Deployed on Streamlit Cloud for easy access"
   - "Available at a public URL for anyone to try"

---

## 📊 Key Features to Demo

- **User Input**: Clean, intuitive symptom entry
- **Progress Tracking**: Real-time status updates
- **Multi-Agent Coordination**: Watch 5 specialized agents work together
- **Comprehensive Results**:
  - Potential conditions with medical literature
  - Clinical trials with locations
  - Specialist recommendations
  - Community resources
  - Next steps for patients
- **Medical Disclaimer**: Ethical compliance

---

## 🔒 Security Best Practices

- ✅ Never commit API keys to GitHub
- ✅ Use environment variables or secrets management
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate API keys periodically
- ✅ Monitor usage to detect anomalies

---

Good luck with your deployment! 🎉
