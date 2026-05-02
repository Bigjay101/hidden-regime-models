import pandas as pd
import json
import os
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
BASE_DIR = "/home/jtshi/school/honours/PGM/hidden-regime-models/data"
MATCHES_FILE = os.path.join(BASE_DIR, "matches/2/27.json")
EVENTS_DIR = os.path.join(BASE_DIR, "events")
LEICESTER_ID = 22

def get_single_match_stats(match_id):
    """Processes a single event file to extract tactical observations for PGM modeling."""
    event_file = os.path.join(EVENTS_DIR, f"{match_id}.json")
    
    if not os.path.exists(event_file):
        return None
        
    with open(event_file, 'r') as f:
        events = pd.json_normalize(json.load(f))
        #print(events.columns)
    
    # Isolate Leicester actions
    lcfc_events = events[events['possession_team.id'] == LEICESTER_ID].copy()
    #print(lcfc_events)
    if lcfc_events.empty:
        return None

    # 1. Attacking Regime Observations
    # Extract StatsBomb xG (numeric)
    total_xg = lcfc_events['shot.statsbomb_xg'].sum() if 'shot.statsbomb_xg' in lcfc_events.columns else 0
    
    # Transition Velocity: Average Carry Distance
    # Carry events now include end_location in v4.0.0[cite: 1]
    carries = lcfc_events[lcfc_events['type.name'] == 'Carry'].copy()
    if not carries.empty and 'carry.end_location' in carries.columns:
        # Calculate distance: simple x-progression[cite: 1]
        carries['dist'] = carries.apply(lambda row: row['carry.end_location'][0] - row['location'][0], axis=1)
        avg_carry_progression = carries['dist'].mean()
        #print(avg_carry_progression)
    else:
        avg_carry_progression = 0

    # 2. Defensive Regime Observations[cite: 1]
    # Extract Counterpress actions (pressing within 5s of turnover)[cite: 1]
    # This attribute exists on pressure, duel, and block events in v4.0.0[cite: 1]
    cp_col = 'counterpress' # Usually flattens to this or 'pressure.counterpress'
    counterpress_count = 0
    for col in [c for c in lcfc_events.columns if 'counterpress' in c]:
        counterpress_count += lcfc_events[col].fillna(False).sum()

    # Defensive Height: Location of all defensive events[cite: 1]
    def_types = ['Pressure', 'Interception', 'Duel', 'Block', 'Foul Committed']#[cite: 1]
    defensive_actions = lcfc_events[lcfc_events['type.name'].isin(def_types)]
    
    if not defensive_actions.empty:
        avg_def_height = defensive_actions['location'].apply(lambda x: x[0]).mean()
    else:
        avg_def_height = 0

    # 3. Structural Observations[cite: 1]
    # Get the starting formation for the match[cite: 1]
    formation = events[events['type.name'] == 'Starting XI']['tactics.formation'].iloc[0] if 'tactics.formation' in events.columns else "Unknown"

    return {
        'match_id': match_id,
        'formation': formation,
        'total_xg': total_xg,
        'counterpress_actions': counterpress_count,
        'avg_def_height': avg_def_height,
        'carry_progression': avg_carry_progression,
        'pass_count': len(lcfc_events[lcfc_events['type.name'] == 'Pass'])
    }

print(get_single_match_stats(3753982))