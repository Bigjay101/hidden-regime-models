import pandas as pd

def getMatchData():
    path = "../data/raw/"
    seasons = [
        '2000-01','2001-02','2002-03','2003-04','2004-05','2005-06',
        '2006-07','2007-08','2008-09','2009-10','2010-11','2011-12',
        '2012-13','2013-14','2014-15','2015-16','2016-17','2017-18',
        '2018-19','2020-2021','2021-2022'
    ]
    drop_cols = ['AvgC<2.5', 'AHCh', 'B365CAHH', 'B365CAHA', 'PCAHH', 'PCAHA', 'MaxCAHH', 'MaxCAHA', 'AvgCAHH', 'AvgCAHA','AvgCH', 'AvgCD', 'AvgCA', 'B365C>2.5', 'B365C<2.5', 'PC>2.5', 'PC<2.5', 'MaxC>2.5', 'MaxC<2.5', 'AvgC>2.5','IWCA', 'WHCH', 'WHCD', 'WHCA', 'VCCH', 'VCCD', 'VCCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD', 'B365CA', 'BWCH', 'BWCD', 'BWCA', 'IWCH', 'IWCD','Max<2.5', 'Avg>2.5', 'Avg<2.5', 'AHh', 'B365AHH', 'B365AHA', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA','B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'GBH', 'GBD', 'GBA', 'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA', 'SBH', 'SBD', 'SBA', 'WHH', 'WHD', 'WHA', 'SJH', 'SJD', 'SJA', 'VCH', 'VCD', 'VCA', 'BSH', 'BSD', 'BSA', 'Bb1X2', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbOU', 'BbMx>2.5', 'BbAv>2.5', 'BbMx<2.5', 'BbAv<2.5', 'BbAH', 'BbAHh', 'BbMxAHH', 'BbAvAHH', 'BbMxAHA', 'BbAvAHA', 'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'Time', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA', 'B365>2.5', 'B365<2.5', 'P>2.5', 'P<2.5', 'Max>2.5','Season','Div','HTHG', 'HTAG','HTR','Referee','HST','AST','AHW','HHW','Attendance']

    frames = []

    # ---------------------------
    # 1. LOAD DATA
    # ---------------------------
    for season in seasons:
        try:
            curr_df = pd.read_csv(f"{path}{season}.csv")
            curr_df["Season"] = season
            frames.append(curr_df)
        except FileNotFoundError:
            print(f"Missing: {season}")

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df = df.copy()  # defragment

    # ---------------------------
    # 2. PARSE DATE & SORT CHRONOLOGICALLY
    # ---------------------------
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df = df.sort_values("Date").reset_index(drop=True)

    # ---------------------------
    # 3. COMPUTE POINTS
    # ---------------------------
    home_points = df["FTR"].map({"H": 3, "D": 1, "A": 0})
    away_points = df["FTR"].map({"A": 3, "D": 1, "H": 0})

    # ---------------------------
    # 4. ROLLING FORM OVER ALL MATCHES (HOME + AWAY)
    # ---------------------------
    home_records = df[["Date", "HomeTeam"]].copy()
    home_records["Team"] = df["HomeTeam"]
    home_records["Points"] = home_points.values

    away_records = df[["Date", "AwayTeam"]].copy()
    away_records["Team"] = df["AwayTeam"]
    away_records["Points"] = away_points.values

    all_records = pd.concat(
        [home_records[["Date", "Team", "Points"]],
         away_records[["Date", "Team", "Points"]]]
    ).sort_values("Date").reset_index(drop=True)

    all_records["Form"] = (
        all_records.groupby("Team")["Points"]
        .rolling(5, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    form_lookup = all_records.set_index(["Date", "Team"])["Form"]

    home_form = pd.Index(zip(df["Date"], df["HomeTeam"])).map(form_lookup)
    away_form = pd.Index(zip(df["Date"], df["AwayTeam"])).map(form_lookup)

    # ---------------------------
    # 5. CONCAT ALL NEW COLUMNS AT ONCE
    # ---------------------------
    new_cols = pd.DataFrame({
        "HomePoints":   home_points.values,
        "AwayPoints":   away_points.values,
        "HomeForm":     home_form,
        "AwayForm":     away_form,
        "HomeForm_cat": pd.qcut(home_form, 3, labels=["low", "mid", "high"]),
        "AwayForm_cat": pd.qcut(away_form, 3, labels=["low", "mid", "high"]),
    }, index=df.index)

    df = pd.concat([df, new_cols], axis=1)

    # ---------------------------
    # 6. DROP UNUSED COLUMNS & DEFRAG
    # ---------------------------
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    df = df.copy()

    return df

def getOldera():
    path = "../data/raw/"
    seasons = [
        '2000-01','2001-02','2002-03','2003-04','2004-05','2005-06',
        '2006-07','2007-08','2008-09','2009-10','2010-11'
    ]
    drop_cols = ['AvgC<2.5', 'AHCh', 'B365CAHH', 'B365CAHA', 'PCAHH', 'PCAHA', 'MaxCAHH', 'MaxCAHA', 'AvgCAHH', 'AvgCAHA','AvgCH', 'AvgCD', 'AvgCA', 'B365C>2.5', 'B365C<2.5', 'PC>2.5', 'PC<2.5', 'MaxC>2.5', 'MaxC<2.5', 'AvgC>2.5','IWCA', 'WHCH', 'WHCD', 'WHCA', 'VCCH', 'VCCD', 'VCCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD', 'B365CA', 'BWCH', 'BWCD', 'BWCA', 'IWCH', 'IWCD','Max<2.5', 'Avg>2.5', 'Avg<2.5', 'AHh', 'B365AHH', 'B365AHA', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA','B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'GBH', 'GBD', 'GBA', 'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA', 'SBH', 'SBD', 'SBA', 'WHH', 'WHD', 'WHA', 'SJH', 'SJD', 'SJA', 'VCH', 'VCD', 'VCA', 'BSH', 'BSD', 'BSA', 'Bb1X2', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbOU', 'BbMx>2.5', 'BbAv>2.5', 'BbMx<2.5', 'BbAv<2.5', 'BbAH', 'BbAHh', 'BbMxAHH', 'BbAvAHH', 'BbMxAHA', 'BbAvAHA', 'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'Time', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA', 'B365>2.5', 'B365<2.5', 'P>2.5', 'P<2.5', 'Max>2.5','Season','Div','HTHG', 'HTAG','HTR','Referee','HST','AST','AHW','HHW','Attendance']

    frames = []

    # ---------------------------
    # 1. LOAD DATA
    # ---------------------------
    for season in seasons:
        try:
            curr_df = pd.read_csv(f"{path}{season}.csv")
            curr_df["Season"] = season
            frames.append(curr_df)
        except FileNotFoundError:
            print(f"Missing: {season}")

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df = df.copy()  # defragment

    # ---------------------------
    # 2. PARSE DATE & SORT CHRONOLOGICALLY
    # ---------------------------
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df = df.sort_values("Date").reset_index(drop=True)

    # ---------------------------
    # 3. COMPUTE POINTS
    # ---------------------------
    home_points = df["FTR"].map({"H": 3, "D": 1, "A": 0})
    away_points = df["FTR"].map({"A": 3, "D": 1, "H": 0})

    # ---------------------------
    # 4. ROLLING FORM OVER ALL MATCHES (HOME + AWAY)
    # ---------------------------
    home_records = df[["Date", "HomeTeam"]].copy()
    home_records["Team"] = df["HomeTeam"]
    home_records["Points"] = home_points.values

    away_records = df[["Date", "AwayTeam"]].copy()
    away_records["Team"] = df["AwayTeam"]
    away_records["Points"] = away_points.values

    all_records = pd.concat(
        [home_records[["Date", "Team", "Points"]],
         away_records[["Date", "Team", "Points"]]]
    ).sort_values("Date").reset_index(drop=True)

    all_records["Form"] = (
        all_records.groupby("Team")["Points"]
        .rolling(5, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    form_lookup = all_records.set_index(["Date", "Team"])["Form"]

    home_form = pd.Index(zip(df["Date"], df["HomeTeam"])).map(form_lookup)
    away_form = pd.Index(zip(df["Date"], df["AwayTeam"])).map(form_lookup)

    # ---------------------------
    # 5. CONCAT ALL NEW COLUMNS AT ONCE
    # ---------------------------
    new_cols = pd.DataFrame({
        "HomePoints":   home_points.values,
        "AwayPoints":   away_points.values,
        "HomeForm":     home_form,
        "AwayForm":     away_form,
        "HomeForm_cat": pd.qcut(home_form, 3, labels=["low", "mid", "high"]),
        "AwayForm_cat": pd.qcut(away_form, 3, labels=["low", "mid", "high"]),
    }, index=df.index)

    df = pd.concat([df, new_cols], axis=1)

    # ---------------------------
    # 6. DROP UNUSED COLUMNS & DEFRAG
    # ---------------------------
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    df = df.copy()

    return df

def getNewEra():
        path = "../data/raw/"
        seasons = [
            '2011-12',
            '2012-13','2013-14','2014-15','2015-16','2016-17','2017-18',
            '2018-19','2020-2021','2021-2022'
        ]
        drop_cols = ['AvgC<2.5', 'AHCh', 'B365CAHH', 'B365CAHA', 'PCAHH', 'PCAHA', 'MaxCAHH', 'MaxCAHA', 'AvgCAHH', 'AvgCAHA','AvgCH', 'AvgCD', 'AvgCA', 'B365C>2.5', 'B365C<2.5', 'PC>2.5', 'PC<2.5', 'MaxC>2.5', 'MaxC<2.5', 'AvgC>2.5','IWCA', 'WHCH', 'WHCD', 'WHCA', 'VCCH', 'VCCD', 'VCCA', 'MaxCH', 'MaxCD', 'MaxCA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD', 'B365CA', 'BWCH', 'BWCD', 'BWCA', 'IWCH', 'IWCD','Max<2.5', 'Avg>2.5', 'Avg<2.5', 'AHh', 'B365AHH', 'B365AHA', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA','B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'GBH', 'GBD', 'GBA', 'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA', 'SBH', 'SBD', 'SBA', 'WHH', 'WHD', 'WHA', 'SJH', 'SJD', 'SJA', 'VCH', 'VCD', 'VCA', 'BSH', 'BSD', 'BSA', 'Bb1X2', 'BbMxH', 'BbAvH', 'BbMxD', 'BbAvD', 'BbMxA', 'BbAvA', 'BbOU', 'BbMx>2.5', 'BbAv>2.5', 'BbMx<2.5', 'BbAv<2.5', 'BbAH', 'BbAHh', 'BbMxAHH', 'BbAvAHH', 'BbMxAHA', 'BbAvAHA', 'PSH', 'PSD', 'PSA', 'PSCH', 'PSCD', 'PSCA', 'Time', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA', 'B365>2.5', 'B365<2.5', 'P>2.5', 'P<2.5', 'Max>2.5','Season','Div','HTHG', 'HTAG','HTR','Referee','HST','AST','AHW','HHW','Attendance']

        frames = []

    # ---------------------------
    # 1. LOAD DATA
    # ---------------------------
        for season in seasons:
            try:
                curr_df = pd.read_csv(f"{path}{season}.csv")
                curr_df["Season"] = season
                frames.append(curr_df)
            except FileNotFoundError:
                print(f"Missing: {season}")

        if not frames:
            return pd.DataFrame()

        df = pd.concat(frames, ignore_index=True)
        df = df.copy()  # defragment

        # ---------------------------
        # 2. PARSE DATE & SORT CHRONOLOGICALLY
        # ---------------------------
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        df = df.sort_values("Date").reset_index(drop=True)

        # ---------------------------
        # 3. COMPUTE POINTS
        # ---------------------------
        home_points = df["FTR"].map({"H": 3, "D": 1, "A": 0})
        away_points = df["FTR"].map({"A": 3, "D": 1, "H": 0})

        # ---------------------------
        # 4. ROLLING FORM OVER ALL MATCHES (HOME + AWAY)
        # ---------------------------
        home_records = df[["Date", "HomeTeam"]].copy()
        home_records["Team"] = df["HomeTeam"]
        home_records["Points"] = home_points.values

        away_records = df[["Date", "AwayTeam"]].copy()
        away_records["Team"] = df["AwayTeam"]
        away_records["Points"] = away_points.values

        all_records = pd.concat(
            [home_records[["Date", "Team", "Points"]],
            away_records[["Date", "Team", "Points"]]]
        ).sort_values("Date").reset_index(drop=True)

        all_records["Form"] = (
            all_records.groupby("Team")["Points"]
            .rolling(5, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        form_lookup = all_records.set_index(["Date", "Team"])["Form"]

        home_form = pd.Index(zip(df["Date"], df["HomeTeam"])).map(form_lookup)
        away_form = pd.Index(zip(df["Date"], df["AwayTeam"])).map(form_lookup)

        # ---------------------------
        # 5. CONCAT ALL NEW COLUMNS AT ONCE
        # ---------------------------
        new_cols = pd.DataFrame({
            "HomePoints":   home_points.values,
            "AwayPoints":   away_points.values,
            "HomeForm":     home_form,
            "AwayForm":     away_form,
            "HomeForm_cat": pd.qcut(home_form, 3, labels=["low", "mid", "high"]),
            "AwayForm_cat": pd.qcut(away_form, 3, labels=["low", "mid", "high"]),
        }, index=df.index)

        df = pd.concat([df, new_cols], axis=1)

        # ---------------------------
        # 6. DROP UNUSED COLUMNS & DEFRAG
        # ---------------------------
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])
        df = df.copy()

        return df


if __name__ == "__main__":
    df = getMatchData()
    print(df.head(20))