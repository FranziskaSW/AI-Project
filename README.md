# Bike Sharing Demand with Decision Trees and Neural Network

The project on GitHub: https://github.com/kfir1g/AI-Project

Within this project you can find:
* Data import, cleaning and feature extraction
* Trees generator: Entropy, Information Gain, Information Ratio  
* ANN jupyter notebook for random forest
* Visualization tools: tree explorer, demand evolvement simulator

## Data import, cleaning and feature extraction
* `data_processing-final.ipynb`  is a Jupyter notebook that cleans the data and extracts feature to generate the trees with.
* `get_data.py`  downloading raw data from [Capital Bikeshare](https://www.capitalbikeshare.com/)
* `get_weather_data.py`  crawl historical weather data for Washington DC area.

All data files can be found [here](https://hey.ichhabeeine.cloud/index.php/s/B8LDtGbjpYbgXek) (password: AI)

## Trees generator
* `tree.py`  includes general implementation of Tree data structure as well as Entropy tree, Information Gain tree and Information Ratio tree representations. 
* `create_train_trees.ipynb` is a file contains the tree creation, as well as creating a file in the required format for the ANN.
* `Create_random_forest.ipynb`  Calculate the results of a random forest with uniform distribution over the weights.

## Neural Network for Random Forest
* `ANN.ipynb`  is a neural network architecture and training script for weighting the likelihood of set of trees (a.k.a random forest) 

## Visualization Tools

#### How to run?
Install Bokeh first: `pip install bokeh`. 

### Tree explorer
To visualize some of the trees we've generated:
```
bokeh serve --show tree_explorer.py
```

### Demand Evolvement Simulator
To see how predicted demand is evolved during the day in dynamic timeline: 
```
bokeh serve --show demand_evolvement.py
```

