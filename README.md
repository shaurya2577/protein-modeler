# Protein-protein interaction explorer

In this project for CalHacks 2025, we train an ML classifier model to predict whether or not 2 proteins interact favorably with each other.

## Getting started

To get started, first set up the virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Then you can install the dependencies:

```
pip install -r requirements.txt
```

To prepare the dataset, run the following script:

```
python -m protein_modeler.data_prepare
```

## Dataset (TBD)

### Bright Data

Option 1 is to use Bright Data which is an AI service provided by one of the Hackathon sponsors, which apparently scours the internet to curate a dataset.

### InAct database

Option 2 is to use the [InAct cancer database](https://www.ebi.ac.uk/intact/search?query=annot:%22dataset:cancer%22). This one has classification data which we can train on, but there is the issue of negative results. As a simple approach, we can just randomly select 2 proteins in our dataset, make sure there isn't positive interaction in our dataset, and then use that as the negative sample.

The dataset we used is a subset of the InAct cancer curated dataset. We used the following filters to create an overall dataset of 6151 samples (before filtering):

- Species is Homo sapiens, 
- Interaction type is positive and negative
- Interactions only between proteins
- Interaction type is physical association


## Acknowledgements

Thanks to [upimapi](https://github.com/iquasere/UPIMAPI) for a helpful batch query API.