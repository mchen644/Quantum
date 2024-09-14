import cirq
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import math
import pickle
import pandas as pd
import os

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

def grover_algorithm(n_qubits, target_states, iterations, num_repititions=int(1e6)):
    

    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()

    circuit.append(cirq.H.on_each(*qubits))

    oracle = grover_oracle(n_qubits, target_states)
    diff = diffuser(n_qubits)

    for _ in range(iterations):
        circuit.append(oracle)
        circuit.append(diff)

    circuit.append(cirq.measure(*qubits, key='result'))
    num_repititions = num_repititions
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=num_repititions)

    result_counts = Counter(result.data['result'].astype(str))

    frequencies = {state: count / num_repititions for state, count in result_counts.items()}
    return frequencies, target_states, num_repititions