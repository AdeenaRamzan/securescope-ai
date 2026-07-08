from huggingface_hub import HfApi
import os

token = input("Paste HuggingFace Write Token: ").strip()
api = HfApi(token=token)

REPO = "AdeenaRamzan93/securescope-ai-api"

FILES = [
     # Docker
    ("Dockerfile", "Dockerfile"),
    # API
    ("backend/src/api/main.py", "src/api/main.py"),

    # Phase 3
    ("backend/src/core/phase3_pipeline.py", "src/core/phase3_pipeline.py"),

    # Requirements
    ("backend/requirements_api.txt", "requirements_api.txt"),

    # CodeBERT
    ("backend/models/saved/codebert_binary/config.json", "models/saved/codebert_binary/config.json"),
    ("backend/models/saved/codebert_binary/model.safetensors", "models/saved/codebert_binary/model.safetensors"),
    ("backend/models/saved/codebert_binary/tokenizer.json", "models/saved/codebert_binary/tokenizer.json"),
    ("backend/models/saved/codebert_binary/tokenizer_config.json", "models/saved/codebert_binary/tokenizer_config.json"),
    ("backend/models/saved/codebert_binary/special_tokens_map.json", "models/saved/codebert_binary/special_tokens_map.json"),
    ("backend/models/saved/codebert_binary/vocab.json", "models/saved/codebert_binary/vocab.json"),
    ("backend/models/saved/codebert_binary/merges.txt", "models/saved/codebert_binary/merges.txt"),

    # RAG
    ("backend/models/saved/owasp_faiss.index", "models/saved/owasp_faiss.index"),
    ("backend/models/saved/owasp_metadata.pkl", "models/saved/owasp_metadata.pkl"),
    ("backend/models/saved/chunk_metadata.json", "models/saved/chunk_metadata.json"),
]

print("\nUploading files...\n")

for local_path, remote_path in FILES:
    if os.path.exists(local_path):
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=remote_path,
            repo_id=REPO,
            repo_type="space",
        )
        print(f"✓ {remote_path}")
    else:
        print(f"✗ Missing: {local_path}")

print("\nDeployment triggered.")
print(f"https://huggingface.co/spaces/{REPO}")