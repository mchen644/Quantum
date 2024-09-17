from grover import *
import random
import time
import multiprocessing
import os
import random
import math
import numpy as np
import random
import math
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import os



def save_pickle(frequencies, data_dict, n_qubit, num_target):
    probs = {}

    for state, freq in frequencies.items():
        state_decimal_num = int(state)
        binary_str = bin(state_decimal_num)[2:]
        probs[binary_str.zfill(n_qubit)] = float(freq)

    data_dict['probs'] = probs

    decimal_list = sorted(int(binary_str, 2) for binary_str in data_dict['marked_status'])
    file_name = "_".join(str(num) for num in decimal_list) + ".pkl"

    os.makedirs('dataset', exist_ok=True)
    os.makedirs(f'dataset/{n_qubit}_qubits_{num_target}_marked', exist_ok=True)
    pd.to_pickle(data_dict, os.path.join(f'dataset/{n_qubit}_qubits_{num_target}_marked', file_name))

def run_grover_simulation(n_qubit, marked_states, SHOTS, num_target):
    iterations = math.floor(np.pi / 4 * np.sqrt(2**n_qubit / len(marked_states)))
    frequencies, targets, num_repititions = grover_algorithm(n_qubit, marked_states, iterations, SHOTS)
    save_pickle(frequencies, {'marked_status': marked_states}, n_qubit, num_target)
    return frequencies, targets


def generate_random_targets(n_qubit, num_target, max_combinations):
    all_targets = []
    for _ in range(max_combinations):
        target_states = []
        for _ in range(num_target):
            target_state = ''.join(random.choice('01') for _ in range(n_qubit))
            while target_state in target_states: 
                target_state = ''.join(random.choice('01') for _ in range(n_qubit))
            target_states.append(target_state)
        all_targets.append(target_states)
    return all_targets

def run_all_simulations(n_qubits, number_targets, samples_per_N_M=5, SHOTS=1_000_000, max_combinations=1000):
    num_cpus = os.cpu_count() // 2  
    
    for n_qubit in n_qubits:
        for num_target in number_targets:
            start_time = time.time()
            print(f'Generating random target combinations for N={n_qubit}, M={num_target}...')
            all_targets = generate_random_targets(n_qubit, num_target, samples_per_N_M)
            
            print(f'Running simulations for N={n_qubit}, M={num_target}...')
            
            with ProcessPoolExecutor(max_workers=num_cpus) as executor:
                futures = [
                    executor.submit(run_grover_simulation, n_qubit, set(target_combination), SHOTS, num_target)
                    for target_combination in all_targets
                ]
                
                for future in as_completed(futures):
                    try:
                        future.result() 
                    except Exception as exc:
                        print(f'Generated an exception: {exc}')
            end_time = time.time()
            duration = end_time - start_time
            print(f'Time taken for N={n_qubit}, M={num_target}: {duration:.2f} seconds')

if __name__ == '__main__':
    n_qubits = [i for i in range(10, 21)]
    number_targets = [i for i in range(1, 33)]
    samples_per_N_M = 128   
    SHOTS = int(1e6)

    run_all_simulations(n_qubits, number_targets, samples_per_N_M, SHOTS)


