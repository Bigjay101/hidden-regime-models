import numpy as np
import pandas as pd
#from 
from data import getMatchData
from features import build_team_view

if __name__ == "__main__":
    matchData = getMatchData()  
    
    print(matchData.dtypes)

