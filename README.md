# Bike Sharing Demand with Decision Trees and Neural Network

Within this project you can find:
* Import data scripts
* Data cleaning and feature extraction
* Trees generator: Entropy, Information Gain, Information Ratio  
* ANN training script for random forest
* Visualization tools: tree explorer, demand evolvement simulator

#### Within this project you can find
  * [Import data scripts](#Import data scripts)
  * [Data cleaning and feature extraction](#Data cleaning and feature extraction)
  * [Trees generator and Random Forest](#Trees generator)
  * [ANN training script for random forest](#Neural Network for Random Forest)
  * [Visualization Tools](#Visualization tools)

## Import data scripts
* `get_data.py` - downloading raw data from [Capital Bikeshare](https://www.capitalbikeshare.com/)
* `get_weather_data.py` - crawl historical weather data for Washington DC area.

## Data cleaning and feature extraction
* `data_processing-final.ipynb` - is a Jupyter notebook that cleans the data and extract feature to generat the trees upon.

## Trees generator
* `tree.py` - includes general implementation of Tree data structure as well as Entropy tree, Information Gain tree and Information Ratio tree representation. 
* `create_train_trees.ipynb`, `Create_random_forest.ipynb` - are files for random forest generation.

## Neural Network for Random Forest
* `ann.py` - is a neural network architecture and training script for weighting the likelihood of set of trees (a.k.a random forest) 

## Visualization Tools

#### How to run?
Install Bokeh first: `pip install bokeh`. 

### Tree explorer
```
bokeh serve --show tree_explorer.py
```

### Demand Evolvement Simulator
```
bokeh serve --show demand_evolvement.py
```

