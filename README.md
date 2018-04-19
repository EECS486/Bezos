### Instillation Instructions

#### Clone the repository 
Make a directory 

`git clone https://github.com/EECS486/Project.git`

#### Install Virtual Env 
Virtual Env acts as a virtual enviornment so that we can virtually install python packages and not overwrite the ones 
on our system 

`pip install virtualenv`

#### Create Virtual Env and Enter it 
Go to your directory where you cloned the repository 

`$ cd Project`

`$ virtualenv env`

`$ source env/bin/activate`

#### Install the requirements
    - Make sure in home directory 

`pip install -r requirements.txt`

#### Deactivate the Virtual ENV
`$ deactivate`

##### Extra: If You Want to Install A New Package
`$ source bin/activate`

`pip install package`

`pip freeze > requirements.txt`

`$ deactivate`

### File + Folder Descriptions

data_analytics_erneh.py - displays analytics for the review and metadata data 
jsonReviewRead.py - review parser for classification models
jsonReviewRead_vBlackfyre.py - review parser for classification models 
metadata.py - metadata parser for classification models
naivebayes.py - naivebayes model classifer 
porter.py - porter stemmer 
reviewdata.py - reviewer parser for naive bayes model
reviewdataNB.py - review parser for naive bayes model 
linking_and_metrics.py - links the metadata and review data and calculates analytics for each review
modelGeneration.py - generates each classification model and projects helpfulness of amazon reviews 

output/ - output for naive bayes and classification models
plots/ - plots for feature importance 

### Instructions 

1. Download and Extract the contents of this folder into the repository
- It contains the json review and metadata files used to generate the review data along with pickle files to make the model generation faster

## Naive Bayes 
1. Open Naive Bayes
2. set the line: params = {"stem": False, "stop": True, "condProb": True, 'bigram': True} to what parameters you want to run the naive bayes with 
- Stem: stems words
- stop: remove stop words
- condProb: generate conditional probabilities 
- bigram: creates a bigram model instead of a unigram model

## Classification Models 
1. In linking_and_metrics.py 
- Set category to the category you want to process. ie: 'Grocery_and_Gourmet_Food'
2. Run data_analytics_erneh.py to generate statics on the whole review set 
2. In modelGeneration.py
- Set category to the category you want to process. ie: 'Grocery_and_Gourmet_Food'
- Note: pkl files must be generated for said category 




