import os
import json
import pickle
import numpy as np

def generate_json_from_pkl(data_folder, output_json):
    json_list = []
    
    for file_name in os.listdir(data_folder):
        if file_name.endswith('.pkl') and (file_name.startswith("2_")
                                           or file_name.startswith("3_") 
                                           or file_name.startswith("4_")):
        # if file_name.endswith('.pkl'):
            file_path = os.path.join(data_folder, file_name)

            with open(file_path, 'rb') as f:
                data_dict = pickle.load(f)
            
            for key, value in data_dict.items():
                instruction = " You need to simulate the Quantum Fourier Transform (QFT) algorithm. Given an input, you are required to compute and output the quantum state vector resulting from the QFT.\n"
                input_str = f"N={len(key)}, b={key}"
                output_str = [f"{complex_num.real:.5g}{complex_num.imag:+.5g}j" for complex_num in value] 
                
                json_list.append({
                    "instruction": instruction,
                    "input": input_str,
                    "output": output_str
                })
    
    with open(output_json, 'w') as json_file:
        json.dump(json_list, json_file, indent=4)

data_folder = 'data'  
output_json = 'QFT_dataset_2_3_4.json'  
generate_json_from_pkl(data_folder, output_json)