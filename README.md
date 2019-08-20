# Bike Sharing Demand with Decision Trees and Neural Network

The project is on GitHub: https://github.com/kfir1g/AI-Project
All of the data are in this drive: https://drive.google.com/open?id=1Izq7xP1Z9SsZ2LtPqIdVL7IiRILcL9ex

Within this project you can find:
* Data import, cleaning and feature extraction
* Trees generator: Entropy, Information Gain, Information Ratio  
* ANN jupyter notebook for random forest
* Visualization tools: tree explorer, demand evolvement simulator

## Data import, cleaning and feature extraction
* `get_data.py`  downloading raw data from [Capital Bikeshare](https://www.capitalbikeshare.com/)
* `get_weather_data.py`  crawl historical weather data for Washington DC area.
* `clean_data.py`  is the script that cleans the data and extracts feature to generate the trees with. To run the script download the folder 'data' from the link below and save it in the main folder.

All data files can be found [here](https://drive.google.com/drive/folders/1Izq7xP1Z9SsZ2LtPqIdVL7IiRILcL9ex?usp=sharing)

## Trees generator
* `tree.py`  includes general implementation of Tree data structure as well as Entropy tree, Information Gain tree and Information Ratio tree representations. Each tree contains a recursive builder, pruning, get_value according to a pandas series (line), saving and loading.
* `create_train_trees.ipynb` is a file contains the tree creation, as well as creating a file in the required format for the ANN. It can create trees based on a desired logic, load existing trees, and then generate a file for the ANN, where each line represents the prediction from each tree and the actual demand.
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

