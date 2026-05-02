import kagglehub
import pandas as pd
import os
import json
import shutil

# 1. Configuration for Leicester 2015/16
'''comp_id = 2  # Premier League
season_id = 27 
dataset_handle = "saurabhshahane/statsbomb-football-data"

# 2. Get the match list first
match_file_path = f"data/matches/{comp_id}/{season_id}.json"
local_match_path = kagglehub.dataset_download(dataset_handle, path=match_file_path)
all_matches = pd.read_json(local_match_path)

# 3. Filter correctly for Leicester City
leicester_matches = all_matches[
    (all_matches['home_team'].str.get('home_team_name') == 'Leicester City') | 
    (all_matches['away_team'].str.get('away_team_name') == 'Leicester City')
].copy()

# 4. Fetch "Form" data for each match
# Let's get the first 5 matches as a test to avoid over-requesting
match_ids = leicester_matches['match_id'].tolist()
all_events_list = []

print(f"Extracting form data for {len(match_ids)} matches...")

for m_id in match_ids[:]: # Testing with 5 matches
    # Path to the specific event file (see image_96c518.png structure)
    event_path = f"data/events/{m_id}.json"
    
    # Surgical download of just this match's events
    local_event_path = kagglehub.dataset_download(dataset_handle, path=event_path)
    
    with open(local_event_path, 'r') as f:
        data = json.load(f)
        # Flatten the nested JSON (e.g., 'shot' -> 'shot.statsbomb_xg')
        df_temp = pd.json_normalize(data)
        df_temp['match_id'] = m_id # Keep track of which match this is
        all_events_list.append(df_temp)

# Combine into one massive 'form' DataFrame
leicester_form_data = pd.concat(all_events_list, ignore_index=True)

# 5. Preview key "Form" indicators
print(leicester_form_data[['match_id', 'type.name', 'possession_team.name', 'shot.statsbomb_xg']].head())'''

# Define your local project data directory
local_data_dir = "/home/jtshi/school/honours/PGM/hidden-regime-models/data"
os.makedirs(local_data_dir, exist_ok=True)

# 1. Download the competitions map locally
comp_path = kagglehub.dataset_download("saurabhshahane/statsbomb-football-data", path="data/competitions.json")
shutil.copy(comp_path, os.path.join(local_data_dir, "competitions.json"))

# 2. Download the PL 2015/16 match list locally
match_path = kagglehub.dataset_download("saurabhshahane/statsbomb-football-data", path="data/matches/2/27.json")
# Create the local folder structure
os.makedirs(os.path.join(local_data_dir, "matches/2"), exist_ok=True)
shutil.copy(match_path, os.path.join(local_data_dir, "matches/2/27.json"))

print(f"Essential files copied to: {local_data_dir}")