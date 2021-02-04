# wave_viewer
 
### Install env
1. make matplotlib interactive in jupyter lab
```
conda create --name wave_viewer
conda activate wave_viewer
conda install -c conda-forge jupyterlab ipympl nodejs

jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install jupyter-matplotlib
jupyter nbextension list 

conda install anaconda
```
2. install the latest hdf5storage
```
git clone https://github.com/frejanordsiek/hdf5storage.git
# Go to the top directory of the repository
pip install -e .
```
3. edit _classic_test_patch.mplstyle

jupyter notebook shows error message for matplotlib Bad key “text.kerning_factor”

https://stackoverflow.com/questions/61171307/jupyter-notebook-shows-error-message-for-matplotlib-bad-key-text-kerning-factor
