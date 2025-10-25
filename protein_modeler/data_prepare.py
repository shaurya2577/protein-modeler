import pandas as pd
import random
import requests, sys, json
from time import sleep




def load_initial_data():
    # had to load separate positive/negative samples 
    # because InAct dataset doesn't provide a positive interaction column
    positives = pd.read_table("data/positive.tsv")
    positives["positive"] = True
    negatives = pd.read_table("data/negative.tsv")
    negatives["positive"] = False
    df = pd.concat([positives, negatives])

    # only get the proteins involved (first 2 columns)
    proteins = df.iloc[:, [0, 1, -1]].copy()
    proteins.columns = ["a", "b", "positive"]

    return proteins

def filter_prefix(proteins):

    proteins = proteins.copy()
    # most of the proteins have a "uniprotkb:" prefix, so filter only those
    for col in ["a", "b"]:
        # create a boolean mask where the prefix exists
        mask = proteins[col].str.startswith("uniprotkb:")

        # remove prefix
        proteins[col] = proteins[col].str.removeprefix("uniprotkb:")

        # keep only rows where the prefix existed
        proteins = proteins[mask]

    return proteins

def filter_interaction(proteins):
    # protein interaction (a, b) is the same as (b, a) so filter duplicates
    proteins['pair_set'] = proteins.apply(lambda row: frozenset([row['a'], row['b']]), axis=1)
    unique_pairs = proteins.drop_duplicates(subset=['pair_set'])
    unique_pairs = unique_pairs.drop(["pair_set"], axis=1)
    unique_pairs.to_csv("data/proteins.csv", index=False)

    return unique_pairs



def get_sequence(unique_ids, start_idx=1000, end_idx=1002, sleep_time=1):
    print("Fetching sequence, might take a while...")
    params = {
    "fields": [
        "sequence",
    ]
    }
    headers = {
    "accept": "application/json"
    }
    base_url = "https://rest.uniprot.org/uniprotkb/"

    sequences = {}


    with open(f"data/sequence_map-{start_idx}-{end_idx}.txt", "w") as f:
        # just test a few proteins for now
        for unique_id in unique_ids[start_idx:start_idx+(end_idx-start_idx)]:
            response = requests.get(base_url + unique_id, headers=headers, params=params)
            if not response.ok:
                response.raise_for_status()
                sys.exit()

            data = response.json()

            # print(json.dumps(data, indent=2))

            if "sequence" in data:
                sequences[unique_id] = data["sequence"]["value"]
                print(unique_id, sequences[unique_id], file=f, flush=True)
                sleep(sleep_time)
    
    return sequences
    

def add_negative_samples(seed=1337):

    mapping =  pd.read_csv("data/sequence_map-0-349.txt", sep=r'\s+', names=["id", "sequence"])
    proteins = pd.read_csv("data/proteins.csv")

    unique_ids = pd.unique(proteins[["a", "b"]].values.ravel()).tolist()

    sample = mapping["id"].sample(n=2, random_state=seed)

    import pdb; pdb.set_trace()


def data_prepare():
    """Load raw exported data from InAct dataset
    
    Column headers are the following:

    - ID(s) interactor A
    - ID(s) interactor B
    - Alt. ID(s) interactor A
    - Alt. ID(s) interactor B
    - Alias(es) interactor A
    - Alias(es) interactor B
    - Interaction detection method(s)
    - Publication 1st author(s)	Publication Identifier(s)
    - Taxid interactor A
    - Taxid interactor B
    - Interaction type(s)
    - Source database(s)
    - Interaction identifier(s)
    - Confidence value(s)

    Preparation steps:

    1) Load positive and negative samples and add column for interaction type
    2) Filter proteins that only have "uniprotkb:" prefix and extract just ID part
    3) Create unique interactions, e.g. (a interacts b) is same as (b interacts a)
    4) Get list of protein IDs to query uniprot for sequence
    5) Call Uniprot API endpoint to get sequence for each unique protein ID
    6) Negative sample (TBD in progress)
    """

    proteins = load_initial_data()
    print("Initial protein size: ", proteins.size)
    print(proteins.head(), "\n")
    
    proteins = filter_prefix(proteins)
    print("After filtering uniprot prefix size:", proteins.size)
    print(proteins.head(), "\n")

    unique_pairs = filter_interaction(proteins)
    print("After filtering a->b, b->a interaction size:", unique_pairs.size)
    print(unique_pairs.head(), "\n")
    
    unique_ids = pd.unique(unique_pairs[["a", "b"]].values.ravel())
    print("Number of unique protein ids:", len(unique_ids))
    print(unique_ids[0:5], "\n")

    sequences = get_sequence(unique_ids)
    print("ID to sequence mapping length:", len(sequences))
    print(sequences, "\n")


if __name__ == "__main__":
    data_prepare()