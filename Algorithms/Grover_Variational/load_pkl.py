import os
import pickle

current_folder = os.getcwd()
data_dir = os.path.join(current_folder, "data")
filename = os.path.join(data_dir, "HEA_2_2_20.pkl")
# for filename in os.listdir(current_folder):
#     if filename.endswith('.pkl'):
try:
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print(data)
except Exception as e:
    print(f"Unable to load {filename}: {e}")