# WiD Datathon 2026 - team data loader
# Team data folder: https://drive.google.com/drive/folders/1wxwVkqYD1YA3Acb4H2uqYkRCWdCLc3mI (wid_seed_and_scale)
# Usage in any Colab notebook:
#   !pip install gdown --quiet
#   exec(open('colab_data_loader.py').read())   # or paste this file into a cell
#   qcl_all = load_bulk('QCL')
#
# Setup (once, by Heidi):
# 1. Team folder already exists: wid_seed_and_scale (link above), sharing = Anyone with the link, Viewer.
# 2. Upload datasets by running Seed_and_scale.ipynb / setup_drive_folder.py in a Colab
#    session that has the files; it uploads and prints the FILE_IDS block.
# 3. For each file: right-click > Share > Copy link. The ID is the long string
#    between /d/ and /view in the URL. Paste IDs below and commit this file.
#
# Fallback: if an ID is missing, the loader downloads straight from FAOSTAT.
# Sources log: every dataset here must appear in the notebook sources log the day it is used.

import os, zipfile
import pandas as pd

FILE_IDS = {
    # dataset: Google Drive file ID  (fill these in after upload)
    'QCL':  'PASTE_ID_HERE',   # Production_Crops_Livestock_E_All_Data_(Normalized).zip
    'SDGB': 'PASTE_ID_HERE',   # SDG_BulkDownloads_E_All_Data_(Normalized).zip
    'ET':   'PASTE_ID_HERE',   # Environment_Temperature_change_E_All_Data_(Normalized).zip
    'FBS':  'PASTE_ID_HERE',   # FoodBalanceSheets_E_All_Data_(Normalized).zip
    'PP':   'PASTE_ID_HERE',   # Prices_E_All_Data_(Normalized).zip
    'TM':   'PASTE_ID_HERE',   # Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip  (large, ~500MB)
    'TCL':  'PASTE_ID_HERE',   # Trade_CropsLivestock_E_All_Data_(Normalized).zip (totals + USD values, Shruti's price layer)
    'WFP':  'PASTE_ID_HERE',   # Mekonnen-Hoekstra Report 47 Appendix II (water footprints, xlsx)
}

FAO_FALLBACK = {
    'QCL':  'https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip',
    'SDGB': 'https://bulks-faostat.fao.org/production/SDG_BulkDownloads_E_All_Data_(Normalized).zip',
    'ET':   'https://bulks-faostat.fao.org/production/Environment_Temperature_change_E_All_Data_(Normalized).zip',
    'FBS':  'https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip',
    'PP':   'https://bulks-faostat.fao.org/production/Prices_E_All_Data_(Normalized).zip',
    'TM':   'https://bulks-faostat.fao.org/production/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip',
    'TCL':  'https://bulks-faostat.fao.org/production/Trade_CropsLivestock_E_All_Data_(Normalized).zip',
}


def _fetch(key):
    """Download one dataset zip (Drive first, FAOSTAT fallback). Returns local path."""
    local = f'{key.lower()}_bulk.zip' if key != 'WFP' else 'water_footprints.xlsx'
    if os.path.exists(local):
        return local
    fid = FILE_IDS.get(key, 'PASTE_ID_HERE')
    if fid and fid != 'PASTE_ID_HERE':
        import gdown
        gdown.download(id=fid, output=local, quiet=False)
    elif key in FAO_FALLBACK:
        import urllib.request
        print(f'{key}: no Drive ID set, downloading from FAOSTAT (slower)...')
        urllib.request.urlretrieve(FAO_FALLBACK[key], local)
    else:
        raise FileNotFoundError(f'{key}: no Drive ID and no fallback URL. '
                                'Download manually and place next to the notebook.')
    return local


def load_bulk(key, chunk_filter=None):
    """Load a FAOSTAT bulk dataset as a DataFrame.

    key: one of QCL, SDGB, ET, FBS, PP, TM, TCL
    chunk_filter: optional function(df_chunk) -> df_chunk, applied while streaming.
                  Use for TM (large), e.g. lambda d: d[d['Item Code'] == 44]
    """
    path = _fetch(key)
    with zipfile.ZipFile(path) as z:
        name = [n for n in z.namelist() if n.endswith('.csv') and 'All_Data' in n.replace(' ', '_')][0]
        if chunk_filter is None:
            df = pd.read_csv(z.open(name), encoding='latin-1', low_memory=False)
        else:
            parts = [chunk_filter(c) for c in pd.read_csv(z.open(name), encoding='latin-1',
                                                          low_memory=False, chunksize=1_000_000)]
            df = pd.concat(parts, ignore_index=True)
    print(f'{key}: {len(df):,} rows loaded from {name}')
    return df


def load_water_footprints(sheet_name=0):
    """Load the Mekonnen & Hoekstra Appendix II spreadsheet (once uploaded to Drive)."""
    path = _fetch('WFP')
    return pd.read_excel(path, sheet_name=sheet_name)
