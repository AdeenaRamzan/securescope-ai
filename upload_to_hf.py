from pathlib import Path
import os

from huggingface_hub import HfApi


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
REPO_ID = os.getenv("HF_SPACE_ID", "AdeenaRamzan93/securescope-ai-api")


def main():
    token = os.getenv("HF_TOKEN") or input("HF token: ").strip()
    api = HfApi(token=token)

    api.upload_file(
        path_or_fileobj=str(ROOT / "securescope-ai-api" / "Dockerfile"),
        path_in_repo="Dockerfile",
        repo_id=REPO_ID,
        repo_type="space",
    )
    api.upload_file(
        path_or_fileobj=str(ROOT / "securescope-ai-api" / "requirements_api.txt"),
        path_in_repo="requirements_api.txt",
        repo_id=REPO_ID,
        repo_type="space",
    )
    print("Uploaded Dockerfile and requirements.")

    api.upload_folder(
        folder_path=str(BACKEND / "src"),
        path_in_repo="src",
        repo_id=REPO_ID,
        repo_type="space",
        ignore_patterns=["__pycache__/*", "*.pyc"],
    )
    print("Uploaded backend/src.")

    api.upload_folder(
        folder_path=str(BACKEND / "models" / "saved"),
        path_in_repo="models/saved",
        repo_id=REPO_ID,
        repo_type="space",
        ignore_patterns=["codebert_binary/checkpoint-*/*", "__pycache__/*", "*.pyc"],
    )
    print("Uploaded backend model artifacts.")
    print("Done. Hugging Face will rebuild the Space.")


if __name__ == "__main__":
    main()
