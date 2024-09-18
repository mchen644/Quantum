from qiskit import QuantumCircuit, transpile
# from qiskit import execute
from qiskit_aer import Aer
from qiskit.circuit import Parameter
import numpy as np
import random
from qiskit.quantum_info import Operator
import qiskit.qasm3 as qasm
from qiskit.quantum_info import Pauli
import os
import pickle
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit.visualization import plot_histogram
import numpy as np
from utils import *
from functions import *
from ansatz import *


nums_qubits = [i for i in range(2, 3)]
depths = [i for i in range(1, 2)]
num_samples = 1

"""
    TODO:
    When generating datasets, need to specifically collect the only_grover data
    random_choices = ["Grover"]
"""

random_choices = ["Grover", "HEA", "Random", None]
data_dir = "data"
only_grover = 0
IF_SAVE_PICKLE = 0

# When generating dataset, we reduce the complexity by lowering the precision to , higher value indicates higher precisions
SAVE_PRECISION = 3 
PARAMS_PRECISION = 3
IF_STORE_HAMILTONIAN = 0

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

for sample in range(num_samples):
    for num_qubits in nums_qubits:
        
        random_choices_updated = random_choices
        
        if num_qubits == 1:
            if "Grover" in random_choices_updated:
                random_choices_updated.remove("Grover")
        
        if len(random_choices_updated) == 0:
            print("random choices are empty, continue to the next loop")
            continue
        
        for depth in depths:
            
            if "Grover" in random_choices_updated and len(random_choices) == 1:
                only_grover = 1
                
            data = {}
            hamiltonian = create_random_hamiltonian(num_qubits)
            if IF_STORE_HAMILTONIAN:
                data["H"] = hamiltonian
            
            initial_circuit =  create_random_initial_state(num_qubits, precision=PARAMS_PRECISION)
            if only_grover:
                # Only implement Grover search, the input state should not be in superposition
                while is_superposition_from_circuit(initial_circuit):
                    initial_circuit =  create_random_initial_state(num_qubits, precision=PARAMS_PRECISION)
                depth = 1
                
            hea_circuit, params, target_state = grover_HEA_ansatz(depth=depth, 
                                                    n_qubits=num_qubits,
                                                    precision=PARAMS_PRECISION,
                                                    input_state=initial_circuit,
                                                    random_choices=random_choices_updated,
                                                    circuit=initial_circuit,
                                                    only_grover=only_grover,
                                                    )
            
            bound_circuit = apply_variational_angles(hea_circuit, params, PARAMS_PRECISION)
            output_state = simulate_circuit(bound_circuit)
            expectation_value = calculate_expectation_value(output_state, hamiltonian)
            
            qasm_string = qasm.dumps(bound_circuit, experimental=qasm.ExperimentalFeatures.SWITCH_CASE_V1)
            qasm_string = extract_after_third_newline(qasm_string)
            
            data["random_choices"] = random_choices_updated
            if only_grover:
                data["target_state"] = target_state
            data["num_qubits"] = num_qubits
            data["only_grover"] = only_grover
            data["ansatz"] = qasm_string.replace('\n', ' ')
            data['output state'] = truncate_statevector(output_state, SAVE_PRECISION)
            if IF_STORE_HAMILTONIAN:
                data['Expectation'] = np.round(expectation_value, SAVE_PRECISION)
            
            if IF_SAVE_PICKLE:
                file_name = f"{num_qubits}_{depth}_{sample}" + ".pkl"
                file_path = os.path.join(data_dir, file_name)
                with open(file_path, 'wb') as file:
                    pickle.dump(data, file)
            print(data)
            # print(qasm_string)
            # print(qasm_string.count('\n'))
            
            # print("Output State:", output_state)
            # print("Expectation:", expectation_value)