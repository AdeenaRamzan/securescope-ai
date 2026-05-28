from huggingface_hub import HfApi

token = input("Paste your HuggingFace token: ")

api = HfApi(token=token)

api.upload_file(
    path_or_fileobj="backend/src/core/predictor.py",
    path_in_repo="src/core/predictor.py",
    repo_id="AdeenaRamzan93/securescope-ai-api",
    repo_type="space"
)

print("predictor.py updated on HuggingFace")