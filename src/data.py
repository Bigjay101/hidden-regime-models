from statsbombpy import sb 

competitions = sb.competitions()
#print(competitions.head())
print(competitions[["competition_id", "competition_name", "season_id", "season_name"]].head(10))
prem = competitions[competitions["competition_name"] == "Premier League"]
#print(prem)

comp_id = 2
season_id =  27

matches = sb.matches(competition_id = comp_id,season_id = season_id)
#print(matches.head())
chelsea_matches = matches[
    (matches["home_team"] == "Chelsea") |
    (matches["away_team"] == "Chelsea")
]

#print(chelsea_matches)