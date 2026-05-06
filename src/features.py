import pandas as pd
from data import getMatchData
def build_team_view(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts match-level data into team-level perspective.
    Each match becomes two rows: home view + away view.
    """

    # ---------------------------
    # HOME & AWAY PERSPECTIVES
    # ---------------------------
    shared = {"Date": df["Date"].values}

    home = pd.DataFrame({
        **shared,
        "Team":           df["HomeTeam"].values,
        "Opponent":       df["AwayTeam"].values,
        "GoalsFor":       df["FTHG"].values,
        "GoalsAgainst":   df["FTAG"].values,
        "ShotsFor":       df["HS"].values,
        "ShotsAgainst":   df["AS"].values,
        "CornersFor":     df["HC"].values,
        "CornersAgainst": df["AC"].values,
        "Offsides": df["HO"].values,
        "Fouls" :         df["HF"].values,
        "Yellow":         df["HY"].values,
        "Red":            df["HR"].values,
        "FTR":            df["FTR"].values,
        "Points":         df["FTR"].map({"H": 3, "D": 1, "A": 0}).values,
        "IsHome":         1,
    })

    away = pd.DataFrame({
        **shared,
        "Team":           df["AwayTeam"].values,
        "Opponent":       df["HomeTeam"].values,
        "GoalsFor":       df["FTAG"].values,
        "GoalsAgainst":   df["FTHG"].values,
        "ShotsFor":       df["AS"].values,
        "ShotsAgainst":   df["HS"].values,
        "CornersFor":     df["AC"].values,
        "Offsides": df["AO"].values,
        "CornersAgainst": df["HC"].values,
        "Fouls" :         df["AF"].values,
        "Yellow":         df["AY"].values,
        "Red":            df["AR"].values,
        "FTR":            df["FTR"].values,
        "Points":         df["FTR"].map({"A": 3, "D": 1, "H": 0}).values,
        "IsHome":         0,
    })

    # ---------------------------
    # COMBINE & SORT CHRONOLOGICALLY
    # ---------------------------
    team_df = pd.concat([home, away], ignore_index=True)
    team_df = team_df.sort_values("Date").reset_index(drop=True)

    # ---------------------------
    # ROLLING FORM (CHRONOLOGICAL)
    # ---------------------------
    team_df["Form"] = (
        team_df.groupby("Team")["Points"]
        .rolling(5, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    # ---------------------------
    # DISCRETISE
    # ---------------------------
    team_df["Form_cat"] = pd.qcut(
        team_df["Form"],
        q=3,
        labels=["low", "mid", "high"]
    )

    return team_df

if __name__ == "__main__":
    data = getMatchData()
    build_team_view(data)
    print(data.head(10))