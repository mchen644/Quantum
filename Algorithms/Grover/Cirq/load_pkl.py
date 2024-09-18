import os
import pickle

current_folder = os.getcwd()

for filename in os.listdir(current_folder):
    if filename.endswith('.pkl'):
        file_path = os.path.join(current_folder, filename)
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            if 'probs' in data and not data['probs']:
                os.remove(file_path)
        except Exception as e:
            print(f"Unable to load {file_path}: {e}")