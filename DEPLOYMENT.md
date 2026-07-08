# SecureScope AI Deployment

## Backend: Hugging Face Space

Use a Docker Space for the FastAPI backend.

Required Hugging Face secret:

```text
GROQ_API_KEY=your_groq_key
```

Upload backend files:

```powershell
cd "E:\Portfolio Project 2026\securescope-ai"
.\.venv\Scripts\activate
pip install huggingface_hub
$env:HF_TOKEN="your_huggingface_write_token"
python upload_to_hf.py
```

The Space runs:

```text
uvicorn src.api.main:app --host 0.0.0.0 --port 7860
```

Test after rebuild:

```text
https://YOUR-SPACE-URL.hf.space/health
https://YOUR-SPACE-URL.hf.space/docs
```

## Frontend: Vercel

Deploy the `frontend` folder to Vercel.

Vercel environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://YOUR-SPACE-URL.hf.space
```

Vercel build settings:

```text
Root Directory: frontend
Install Command: npm install
Build Command: npm run build
Output Directory: .next
```

## Important

- Put `GROQ_API_KEY` only in Hugging Face.
- Put `NEXT_PUBLIC_API_BASE_URL` only in Vercel.
- Do not expose Groq keys in frontend code.
