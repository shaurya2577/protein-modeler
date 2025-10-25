Vocab:
Target/Antigen = The protein that the user wants to create a binder for
Can be a human protein (for example, binders to IL-3 protein can help supress an overactive immune system)
Can be an antigen like RBD, the covid spike protein (antibodies that bind to RBD help our body to fight off covid)
Binder/antibody = A protein that binds to the target/antigen
Antibody is a specific type of protein that binds to an antigen
Epitope = What part of the target the binder binds to
Protein Structure = Proteins are made up of a sequence of amino acids. This sequence of amino acids then folds to form the structure of a protein

Project ideas
Cancer protein focus, idea is antibody can be inputted and our program will return all cancer targets this antibody could be used for (repurposability)
Alternatively, look at all human proteins the antibody could bind to for safety purposes
Higher compute, but more useful for clinical trials and potentially better dataset

Dataset ideas
Concerns
There will not be much negative data. Either we will have to generate negative data or try weighting the negative data (depends how badly biased the dataset is, but most likely we will have to generate negative data)
Easiest method, just use random protein-protein pairs that have no recorded positive data
Other methods: Generate negative data using Alphafold or other open source model, choose protein pairs that have low confidence scores to be negative data
Dataset may be biased
Certain targets will have much much more data. Especially when limiting down to only cancer proteins, some of these proteins will have thousands of recorded binders but some will have 0
Cancer dataset posted in slack
Should check for how big the dataset is after filtering, but it looks like solid data with all the info we need
UniProt
Has a lot of proteins in general, I think we can download all the data from just humans. They might also have a curated cancer dataset. Well formated.
Found a dataset from a paper with ~5000 interactions
Some targets definitely have way more recorded interactions than others, and also there is no negative data in this dataset. All binders are FDA approved.


Model ideas:
Protein Structure = Proteins are made up of a sequence of amino acids. This sequence of amino acids then folds to form the structure of a protein
In the context of our project, the sequence of amino acids can be “read” using an LLM model like ESM2
However this would not take into account the structure of a protein. The 3D structure of a protein will bring amino acids close together that may not be neighboring in the linear sequence
Neural networking to take into account amino acid positioning of amino acids that are not neighboring in the sequence
Neural networks of amino acid, all amino acids from target and antibody in a soup and use neural network to decide the weights and relationships between amino acids
Ideally we do want to incorporate the amino acid’s neighbors, maybe some level of sequencing data? There should be kits for this
Maybe we can find epitope and cut down on compute by focusing structural parts of the model on the epitope and using a language model to identify? stuff not sure


