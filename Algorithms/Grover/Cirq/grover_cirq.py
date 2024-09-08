import cirq
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import math

def grover_oracle(n_qubits, target_states):
    oracle_circuit = cirq.Circuit()

    for target_state in target_states:
        temp_circuit = cirq.Circuit()
        for i in range(n_qubits):
            if target_state[i] == '0':
                temp_circuit.append(cirq.X(cirq.LineQubit(i)))

        # Controlled-Z gate for marking the target state
        temp_circuit.append(cirq.Z(cirq.LineQubit(n_qubits - 1)).controlled_by(*cirq.LineQubit.range(n_qubits - 1)))

        for i in range(n_qubits):
            if target_state[i] == '0':
                temp_circuit.append(cirq.X(cirq.LineQubit(i)))

        oracle_circuit += temp_circuit

    return oracle_circuit


def diffuser(n_qubits):
    diffuser_circuit = cirq.Circuit()

    # Apply Hadamard gate to all qubits
    diffuser_circuit.append(cirq.H.on_each(*cirq.LineQubit.range(n_qubits)))

    # Apply X gate to all qubits
    diffuser_circuit.append(cirq.X.on_each(*cirq.LineQubit.range(n_qubits)))

    # Apply multi-controlled Z gate
    diffuser_circuit.append(cirq.Z(cirq.LineQubit(n_qubits - 1)).controlled_by(*cirq.LineQubit.range(n_qubits - 1)))

    # Apply X gate to all qubits
    diffuser_circuit.append(cirq.X.on_each(*cirq.LineQubit.range(n_qubits)))

    # Apply Hadamard gate to all qubits
    diffuser_circuit.append(cirq.H.on_each(*cirq.LineQubit.range(n_qubits)))

    return diffuser_circuit

def grover_algorithm(n_qubits, target_states, iterations):
    

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    circuit.append(cirq.H.on_each(*qubits))

    oracle = grover_oracle(n_qubits, target_states)
    diff = diffuser(n_qubits)

    for _ in range(iterations):
        circuit.append(oracle)
        circuit.append(diff)

    circuit.append(cirq.measure(*qubits, key='result'))
    num_repititions = int(1e6)
    simulator = cirq.Simulator()
    print(num_repititions)
    result = simulator.run(circuit, repetitions=num_repititions)

    result_counts = Counter(result.data['result'].astype(str))

    frequencies = {state: count / num_repititions for state, count in result_counts.items()}
    print(1)
    return frequencies, target_states, num_repititions

import random
n_qubits = [3,4,5,6,7,8,9]
IF_DRAW_FREQUENCES = 1
number_targets = 2
n_qubit_time = {}
for n_qubit in n_qubits:
    target_states = []
    for _ in range(number_targets):
        target_state = ''.join(random.choice('01') for _ in range(n_qubit))
        while target_state in target_states:
            target_state = ''.join(random.choice('01') for _ in range(n_qubit))
        target_states.append(target_state)
    print("target states:", target_states)

    iterations = math.floor(np.pi / 4 * np.sqrt(2**n_qubit/number_targets))
    import time
    st = time.time()
    frequencies, targets, num_repititions = grover_algorithm(n_qubit, target_states, iterations)
    cost_time = time.time() - st
    print(f"The cost time for running {n_qubit} qubits is {cost_time}:")
    n_qubit_time[n_qubit] = cost_time

    for target in targets:
        print(f"Target state: {str(int(target, 2))}")

    for state, freq in frequencies.items():
        print(f"{state}: {freq:.7f}")

    if IF_DRAW_FREQUENCES:
        plt.figure(figsize=(10, 6))
        bars = plt.bar(frequencies.keys(), frequencies.values())
        targets_str = [str(int(x, 2)) for x in targets]
        plt.title(f"Frequencies of States(target states = {targets_str})")
        plt.xlabel("States")
        plt.ylabel("Frequency")

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.7f}', 
                    ha='center', va='bottom')

        plt.savefig(f'frequencies_bar_plot_{n_qubit}.png')

    for target in targets:
        target = str(int(target, 2))
        if target in frequencies:
            print(f"Found the target state {target} with frequency {frequencies[target]:.3f}")
        else:
            print(f"Target state {target} not found.")



def plot_dict_data(data_dict, save_path):
    keys = list(data_dict.keys())
    values = list(data_dict.values())

    plt.figure(figsize=(10, 6))
    plt.plot(keys, values, marker='o', linestyle='-', color='b')
    plt.xlabel('Number of Qubits')
    plt.ylabel('Simulation Time (s)')
    plt.title(f'Number of Repetitions (Shots) = {num_repititions}')
    plt.grid(True)
    
    # Save the plot to the specified path
    plt.savefig(save_path)
    plt.close()

def plot_dict_data_with_comparison(data_dict, save_path):
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    
    # Initialize the comparison values with the first point
    comparison_values = [values[0]]
    
    # Compute the comparison values based on the given formula
    for i in range(1, len(keys)):
        prev_value = comparison_values[i - 1]
        current_key = keys[i]
        prev_key = keys[i - 1]
        new_value = np.sqrt(2**current_key) * prev_value / np.sqrt(2**prev_key)
        comparison_values.append(new_value)

    # Plot the original data
    plt.figure(figsize=(10, 6))
    plt.plot(keys, values, marker='o', linestyle='-', color='b', label='Original Data')

    # Plot the comparison data
    plt.plot(keys, comparison_values, marker='o', linestyle='--', color='r', label='Comparison Data')
    
    plt.xlabel('Number of Qubits')
    plt.ylabel('Simulation Time (s)')
    plt.title('Number of Repetitions (Shots)')
    plt.grid(True)
    plt.legend()

    # Save the plot to the specified path
    plt.savefig(save_path)
    plt.close()

# plot_dict_data_with_comparison(n_qubit_time, "simulation_time_plot.png")

plot_dict_data(n_qubit_time, "simulation_time_plot.png")