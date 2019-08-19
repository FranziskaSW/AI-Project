# Bike Sharing Demand with Decision Trees and Neural Network

Within this project you can find:
* Data import, cleaning and feature extraction
* Trees generator: Entropy, Information Gain, Information Ratio  
* ANN training script for random forest
* Visualization tools: tree explorer, demand evolvement simulator

## Data import, cleaning and feature extraction
* `data_processing-final.ipynb` - is a Jupyter notebook that cleans the data and extracts feature to generate the trees with.
* `get_data.py` - downloading raw data from [Capital Bikeshare](https://www.capitalbikeshare.com/)
* `get_weather_data.py` - crawl historical weather data for Washington DC area.

All data files can be found [here](https://hey.ichhabeeine.cloud/index.php/s/B8LDtGbjpYbgXek) (password: AI)

## Trees generator
* `tree.py` - includes general implementation of Tree data structure as well as Entropy tree, Information Gain tree and Information Ratio tree representations. 
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

