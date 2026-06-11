from huggingface_hub import HfApi

token = input("Token: ")
api = HfApi(token=token)

# Upload new predictor
api.upload_file(
    path_or_fileobj="backend/src/core/predictor_phase2.py",
    path_in_repo="src/core/predictor_phase2.py",
    repo_id="AdeenaRamzan93/securescope-ai-api",
    repo_type="space"
)

# Upload updated main.py
api.upload_file(
    path_or_fileobj="backend/src/api/main.py",
    path_in_repo="src/api/main.py",
    repo_id="AdeenaRamzan93/securescope-ai-api",
    repo_type="space"
)

# Upload model files
import os
model_files = [
    "bilstm_phase2_binary_best.pth",
    "phase2_binary_bilstm_config.json",
    "vocabulary_phase2_binary_bilstm.json"
]

for fname in model_files:
    api.upload_file(
        path_or_fileobj=f"backend/models/saved/{fname}",
        path_in_repo=f"models/saved/{fname}",
        repo_id="AdeenaRamzan93/securescope-ai-api",
        repo_type="space"
    )
    print(f"Uploaded: {fname}")

print("All files uploaded. HuggingFace rebuilding...")