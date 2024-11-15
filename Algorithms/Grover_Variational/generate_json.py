import os
import json
import pickle
import numpy as np

def generate_json_from_pkl(data_folder, output_json):
    json_list = []
    
    for file_name in os.listdir(data_folder):
        if file_name.startswith("2_") or file_name.startswith("3_") or file_name.startswith("4_"):
            file_path = os.path.join(data_folder, file_name)

            with open(file_path, 'rb') as f:
                data_dict = pickle.load(f)
            
            instruction = " Give the output state according to the ansatz description in Qasm format\n"
            input_str = f"N={data_dict['num_qubits']}, ansatz = {data_dict['ansatz']}"
            output_str = f"{[i for i in data_dict['output state']]}"
            json_list.append({
                "instruction": instruction,
                "input": input_str,
                "output": output_str
            })
    
    with open(output_json, 'w') as json_file:
        json.dump(json_list, json_file, indent=4)

data_folder = 'data'  
output_json = 'dataset.json'  
generate_json_from_pkl(data_folder, output_json)