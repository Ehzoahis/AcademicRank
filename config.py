# Congfiguration for some global variables
# Database for saving Keywords (Specific for Haozhe Si)
db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'

# Data number used for tqdm, specific for implementation
FOS_CNT = 741671 # Number of FOS from FieldsOfStudy.txt
PAPERFID_CNT = 1403999324 # Number of PAPER-FId Pairs from PaperFieldsOfStudy.txt
EDGE_CNT = 1670074311 # Number of Reference Relations in PaperReferneces.txt

PRUNED_EDGE_CNT = 1094935127 # Edge number after being pruned
PRUNED_PAPER_CNT = 355977380 # CS Paper number after being pruned

# MAG Dataset Path
mid2fid_fname = './PFoS.txt' # Dataset containing Paper-FId Information
fos_fname = './FieldsOfStudy.txt' # Dataset contianing all the FoS in MAG
mag_db = './PaperReferences.txt' # Dataset containing the citation relationship in MAG

# Output dataset path
cspaper_fname = './cspapers.txt' # Pruned Papers about CS
csedges_fname = './pruned_PR.txt' # Pruned Edges about CS
