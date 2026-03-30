# Hospital Quick Find

A Streamlit application to quickly find the nearest hospital with the shortest estimated wait time.

## Deployment Instructions

### GitHub
This repository is ready to be pushed to GitHub. Make sure your `.gitignore` is correctly configured (it already is) before running:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Streamlit Community Cloud (Recommended)
Streamlit apps are best deployed on [Streamlit Community Cloud](https://streamlit.io/cloud):
1. Push your code to GitHub.
2. Log in to Streamlit Community Cloud.
3. Click **New app**.
4. Select the repository, branch, and set the main file path to `app.py`.
5. Click **Deploy!**

### Vercel
*Note: Streamlit relies on WebSockets and a persistent server, which makes it fundamentally incompatible with Vercel's Serverless Functions architecture. However, the repository has been configured with a `vercel.json` as requested.*

If you plan to use Vercel, it is highly recommended to convert the frontend to React/Next.js and use `hospital_agent.py` wrapped in FastAPI/Flask as the backend API in the `api/` folder.
