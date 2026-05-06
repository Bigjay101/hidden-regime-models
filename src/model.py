from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from networkx.drawing.nx_pydot import graphviz_layout
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from data import getMatchData, getNewEra, getOldera

# ---------------------------
# CONSTANTS
# ---------------------------
MODEL_EDGES = [
    ("HomeForm_cat", "HomeShotsFor"),
    ("HomeForm_cat", "HomeCorners"),
    ("HomeForm_cat", "HomeOffsides"),
    ("HomeForm_cat", "HomeFouls"),
    ("HomeFouls",    "HomeYellow"),
    ("HomeFouls",    "HomeRed"),

    ("AwayForm_cat", "AwayShotsFor"),
    ("AwayForm_cat", "AwayCorners"),
    ("AwayForm_cat", "AwayOffsides"),
    ("AwayForm_cat", "AwayFouls"),
    ("AwayFouls",    "AwayYellow"),
    ("AwayFouls",    "AwayRed"),

    ("HomeShotsFor", "FTR"),
    ("AwayShotsFor", "FTR"),
]

TRAIN_COLS = [
    "HomeForm_cat",  "AwayForm_cat",
    "HomeShotsFor",  "AwayShotsFor",
    "HomeYellow",    "AwayYellow",
    "HomeRed",       "AwayRed",
    "HomeFouls",     "AwayFouls",
    "HomeCorners",   "AwayCorners",
    "HomeOffsides",  "AwayOffsides",
    "FTR",
]

# ---------------------------
# DISCRETISATION
# ---------------------------
def discretise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def qcut(col, new_col):
        if col in df.columns:
            df[new_col] = pd.qcut(df[col], 3, labels=["low", "mid", "high"])
        else:
            print(f"  Skipping '{new_col}' — '{col}' not in dataset")

    def cut(col, new_col, bins, labels):
        if col in df.columns:
            df[new_col] = pd.cut(df[col], bins=bins, labels=labels)
        else:
            print(f"  Skipping '{new_col}' — '{col}' not in dataset")

    qcut("HS", "HomeShotsFor")
    qcut("AS", "AwayShotsFor")
    qcut("HF", "HomeFouls")
    qcut("AF", "AwayFouls")
    qcut("HC", "HomeCorners")
    qcut("AC", "AwayCorners")
    qcut("HO", "HomeOffsides")
    qcut("AO", "AwayOffsides")

    cut("HY", "HomeYellow", [-1, 1, 3, 10], ["low", "mid", "high"])
    cut("AY", "AwayYellow", [-1, 1, 3, 10], ["low", "mid", "high"])
    cut("HR", "HomeRed",    [-1, 0, 1, 10],  ["none", "one", "multi"])
    cut("AR", "AwayRed",    [-1, 0, 1, 10],  ["none", "one", "multi"])

    return df

# ---------------------------
# TRAINING
# ---------------------------
def build_train_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in TRAIN_COLS if c in df.columns]
    return df[cols].dropna().astype(str)


def fit_model(train_df: pd.DataFrame) -> DiscreteBayesianNetwork:
    # Only keep edges where both nodes are present in the data
    available = set(train_df.columns)
    edges = [
        (src, dst) for src, dst in MODEL_EDGES
        if src in available or src in ("HomeForm_cat", "AwayForm_cat")
        if dst in available
    ]

    model = DiscreteBayesianNetwork(edges)
    estimator = MaximumLikelihoodEstimator(model, train_df)
    model.cpds = estimator.get_parameters()
    assert model.check_model(), "Model failed check"
    return model

# ---------------------------
# INFERENCE
# ---------------------------
def run_query(model: DiscreteBayesianNetwork, variables: list, evidence: dict, label: str):
    inference = VariableElimination(model)
    result = inference.query(variables=variables, evidence=evidence, show_progress=False)
    print(f"\n=== {label} ===")
    print(result)
    return result


def plot_model(model: DiscreteBayesianNetwork):
    G = nx.DiGraph(model.edges())
    pos = graphviz_layout(G, prog="dot")
    nx.draw(G, pos, with_labels=True, node_size=3000)
    plt.tight_layout()
    plt.show()

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    evidence = {
        "HomeShotsFor": "high",
        "AwayShotsFor": "low",
        "HomeYellow":   "low",
        "AwayYellow":   "high",
        "HomeFouls": "low",
        "AwayFouls": "high",
        #"HomeCorners": "high",
        #"AwayCorners": "low"
    }

    eras = {
        "All Seasons": getMatchData(),
    }

    models = {}
    for label, raw_df in eras.items():
        print(f"\nFitting: {label}")
        disc_df   = discretise(raw_df)
        train_df  = build_train_df(disc_df)
        models[label] = fit_model(train_df)

    for label, model in models.items():
        run_query(model, variables=["HomeForm_cat"], evidence=evidence, label=label)

    plot_model(models["All Seasons"])