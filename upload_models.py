from huggingface_hub import HfApi
import os

# Get token from hf auth
token = input("Paste your HuggingFace token: ")

api = HfApi(token=token)

print('Uploading models...')
api.upload_folder(
    folder_path='backend/models/saved',
    repo_id='AdeenaRamzan93/securescope-ai-api',
    repo_type='space',
    path_in_repo='models/saved'
)
print('Models uploaded successfully')