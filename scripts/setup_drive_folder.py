# WiD Datathon 2026 - one-time Drive setup (run inside Colab)
#
# What it does, in one run:
#   1. Creates the shared folder "WiD-Datathon-Data" in your Drive (if not already there)
#   2. Sets link-sharing: Anyone with the link, Viewer
#   3. Uploads every dataset file it finds in the Colab session's working directory
#      (skips any file already in the folder, so it is safe to re-run)
#   4. Prints a ready-to-paste FILE_IDS block for colab_data_loader.py
#
# How to run:
#   - In a Colab session where the bulk zips exist (run the notebooks' download cells first,
#     or re-run this later as more datasets arrive)
#   - Paste this whole file into a cell and run it
#   - Click through the one Google auth prompt
#   - Copy the printed FILE_IDS block into colab_data_loader.py and push to the repo
#
# Re-running later with new files just uploads the new ones and reprints the block.

from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

FOLDER_NAME = 'wid_seed_and_scale'
FOLDER_ID = '1wxwVkqYD1YA3Acb4H2uqYkRCWdCLc3mI'   # Heidi's shared team folder; leave set so everyone uploads to the SAME folder.
                                                 # NOTE: uploading into it requires Editor access - Heidi: share the
                                                 # folder with teammates as Editor, not just Viewer, if they will upload.

# local filename -> loader key (must match colab_data_loader.py)
EXPECTED = {
    'qcl_bulk.zip':          'QCL',
    'sdg_bulk.zip':          'SDGB',
    'et_bulk.zip':           'ET',
    'fbs_bulk.zip':          'FBS',
    'pp_bulk.zip':           'PP',
    'tm_bulk.zip':           'TM',
    'tcl_bulk.zip':          'TCL',
    'water_footprints.xlsx': 'WFP',
}

auth.authenticate_user()
drive = build('drive', 'v3')

# 1. Use the pinned team folder if set; otherwise find-or-create by name
if FOLDER_ID:
    folder_id = FOLDER_ID
    info = drive.files().get(fileId=folder_id, fields='name').execute()
    print(f"Using team folder: {info['name']} ({folder_id})")
else:
    q = f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    hits = drive.files().list(q=q, fields='files(id,name)').execute().get('files', [])
    if hits:
        folder_id = hits[0]['id']
        print(f'Folder exists: {FOLDER_NAME} ({folder_id})')
    else:
        meta = {'name': FOLDER_NAME, 'mimeType': 'application/vnd.google-apps.folder'}
        folder_id = drive.files().create(body=meta, fields='id').execute()['id']
        print(f'Created folder: {FOLDER_NAME} ({folder_id})')

# 2. Link-sharing: anyone with the link can view
try:
    drive.permissions().create(fileId=folder_id,
                               body={'type': 'anyone', 'role': 'reader'}).execute()
    print('Sharing set: Anyone with the link, Viewer')
except Exception as e:
    print(f'Sharing unchanged (only the folder owner can set it): {type(e).__name__}')

# 3. Upload whatever expected files are present locally, skipping ones already up
existing = drive.files().list(q=f"'{folder_id}' in parents and trashed=false",
                              fields='files(id,name)').execute().get('files', [])
existing_by_name = {f['name']: f['id'] for f in existing}

file_ids = {}
for fname, key in EXPECTED.items():
    if fname in existing_by_name:
        file_ids[key] = existing_by_name[fname]
        print(f'already in Drive: {fname}')
    elif os.path.exists(fname):
        print(f'uploading {fname} ({os.path.getsize(fname)/1e6:.0f} MB)...')
        media = MediaFileUpload(fname, resumable=True)
        f = drive.files().create(body={'name': fname, 'parents': [folder_id]},
                                 media_body=media, fields='id').execute()
        file_ids[key] = f['id']
        print(f'  done: {fname}')
    else:
        print(f'not found locally, skipping for now: {fname}')

# 4. Print the paste-ready block
print('\n' + '=' * 60)
print('PASTE INTO colab_data_loader.py, replacing FILE_IDS:')
print('=' * 60)
print('FILE_IDS = {')
for fname, key in EXPECTED.items():
    fid = file_ids.get(key, 'PASTE_ID_HERE')
    print(f"    '{key}':  '{fid}',   # {fname}")
print('}')
print('\nFolder link to share in team chat:')
print(f'https://drive.google.com/drive/folders/{folder_id}')
