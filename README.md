# AcademicRank
2021SP FORWARD Lab Project

## Introduction
The goal of the project is to calculate the rank of academic works given a keyword. The rank will be calculated according to the *Field of Study* of the paper. The ranking algorithm is inspired by [The PageRank Citation Ranking: Bringing Order to the Web](http://ilpubs.stanford.edu:8090/422/), with the assumption that similarity between the papers and the target keywords can only be distributed once to speed up the calculation. Currently, the program can only handle the keyword with multiple words to ensure the accuracy of ranking.

## Installation
Install the package using  ```requirements.txt```

```shell
pip3 install -r requirements.txt
```

## Datasets
### Microsoft Academic Graph
The [Mircosoft Academic Graph](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/) is a heterogeneous graph containing scientific publication records, citation relationships between those publications and fields of study. The schema of the dataset can be found [here](https://docs.microsoft.com/en-us/academic-services/graph/reference-data-schema). Among those dataset files, we would use:
- FieldsOfStudy
- PaperFieldsOfStudy
- PaperReferences

The downloaded data can be found on owl3 server, [path](server/scratch/pritom/mag-2020-09-14).

### Springer-83K CS Keywords
The CS keywords collected from Springer by [Yanghui Pang](yanghui2@illinois.edu). Dataset can be found [here](https://github.com/Ehzoahis/AcademicRank/tree/main/dataset).

## word2vec Model
The word2vec model is trained on the abstract of papers in  [arXive](https://arxiv.org/) dataset by [Edward Ma](kcma2@illinois.edu). The model can be found [here](https://github.com/Ehzoahis/AcademicRank/tree/main/word2vec).

## Usage
### Build the Pruned MAG Dataset
To speed up the ranking algorithm, we need to first prune out the Field of Study (FoS) that are not CS keywords.
```python
python3 prune_fos.py
```
The resulting FoS list will be in ```pruned_FOS.txt```.

We further need to prune out the papers and references that do not relate to CS.
```python
python3 prune_paper_edge.py
```
The resulting file are ```cspapers.txt``` and ```pruned_PR.txt```.

*If any issue exists when running* ```prune_fos.py``` *or* ```prune_paper_edge.py``` *please check the [original codes](https://github.com/Ehzoahis/AcademicRank/tree/main/dev_codes/AcademicRank)  which are more stable.*

### Perform AcademicRank
The preparation work only need to be done once. To calculate the rank of papers given keywords, do
```python
python3 academic_rank.py [keyword1,keyword2,...]
```
where keywords need to be separated by ',' and keywords with multiple words need to be connected by '_'. E.g.

```python
python3 academic_rank.py computer_science,data_mining
```

### Visualization
Since the ```academic_rank.py``` will give a list of paper ID, we can find the name of the papers given the ID using MAG API. See methods and examples from ```visualization.ipynb``` for more information.

## Reservation
The accuracy of this program is not guaranteed because the vocabulary of the word2vec model is not large enough and thus the keyword similarity cannot be calculated in the most times. Currently, the program is assigning dummy similarity to the keywords that are not in word2vec model.

## Author
- [Haozhe Si](haozhes3@illinois.edu)
- Instructed by [Professor Kevin Chang](kcchang@illinois.edu)
