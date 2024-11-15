from qiskit import QuantumCircuit, transpile
# from qiskit import execute
from qiskit_aer import Aer
from qiskit.circuit import Parameter
import numpy as np
import random
from qiskit.quantum_info import Operator
import qiskit.qpy as qpy
import qiskit.qasm3 as qasm
from qiskit.quantum_info import Pauli
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate
from qiskit.visualization import plot_histogram
import numpy as np
from utils import *
from functions import *

# Oracle that marks the target states
def grover_oracle(n_qubits, target_states, circuit=None):
    if circuit == None:
        circuit = QuantumCircuit(n_qubits)
        
    if target_states[0] == None:
        return circuit
    
    for target_state in target_states:
        if target_state == "Superposition":
            target_state = ''.join(random.choice(['0', '1']) for _ in range(n_qubits)) 
        reversed_target_state = target_state[::-1]
        for i in range(n_qubits):
            if reversed_target_state[i] == '0':
                circuit.x(i)
        
        # Apply multi-controlled Z gate
        circuit.h(n_qubits-1)
        circuit.mcx(list(range(n_qubits-1)), n_qubits-1)
        circuit.h(n_qubits-1)

        for i in range(n_qubits):
            if reversed_target_state[i] == '0':
                circuit.x(i)

    return circuit

# Diffuser for Grover's algorithm
def diffuser(n_qubits, circuit=None):
    
    if circuit == None:
        circuit = QuantumCircuit(n_qubits)

    # Apply Hadamard to all qubits
    circuit.h(range(n_qubits))

    # Apply X gate to all qubits
    circuit.x(range(n_qubits))

    # Apply multi-controlled Z gate
    # Note, there is no direct multi-controlled Z gate in qiskit
    # Thus we can use the below trick to apply:
    # For 2 or 3 qubits, one can verify it using cz or ccz gate
    circuit.h(n_qubits-1)
    circuit.mcx(list(range(n_qubits-1)), n_qubits-1)
    circuit.h(n_qubits-1)

    # Apply X gate to all qubits
    circuit.x(range(n_qubits))

    # Apply Hadamard to all qubits
    circuit.h(range(n_qubits))

    return circuit

def hea_ansatz(num_qubits, params, depth=1, circuit=None, idx=None):
    if circuit == None:
        circuit = QuantumCircuit(num_qubits)
    
    if params == None:
        params = []

    for d in range(depth):
        for qubit in range(num_qubits):
            theta = Parameter(f'theta_{d}_{qubit}_{idx}')
            circuit.ry(theta, qubit)
            circuit.rz(theta, qubit)  
            params.append(theta)
            
        for i in range(0, num_qubits-1, 2):
            circuit.cx(i, i+1)
        for i in range(1, num_qubits-1, 2):
            circuit.cx(i, i+1)

    return circuit, params

def qaoa_ansatz(num_qubits, params, depth=1, circuit=None, idx=None):
    if circuit == None:
        circuit = QuantumCircuit(num_qubits)
    
    if params == None:
        params = []

    for d in range(depth):
        # Problem unitary (Cost Hamiltonian)
        gamma = Parameter(f'qaoa_gamma_{d}_{idx}')
        beta = Parameter(f'qaoa_beta_{d}_{idx}')

        # Problem unitary (Cost Hamiltonian)
        circuit.rzz(2 * gamma, 0, 1)

        # Mixer unitary
        circuit.rx(2 * beta, 0)
        circuit.rx(2 * beta, 1)
        params.append(gamma)
        params.append(beta)

    return circuit, params

def grover_ansatz(n_qubits, target_states, iterations, circuit=None):
    if circuit == None:
        circuit = QuantumCircuit(n_qubits)
    
    # Initial Hadamard gate on all qubits
    circuit.h(range(n_qubits))

    # Repeat the Grover iteration as needed
    for _ in range(iterations):
        circuit = grover_oracle(n_qubits, target_states, circuit=circuit)
        circuit = diffuser(n_qubits, circuit=circuit)
    return circuit

def random_ansatz(n_qubits, max_operations, precision, circuit=None):
    
    if circuit==None:
        circuit = QuantumCircuit(n_qubits)
        
    n_operations = random.randint(1, max_operations)
    print("Number of operations in current depth = ", n_operations)
    
    for _ in range(n_operations):
        gate_type = random.choice(['x', 'h', 'ry', 'rz', 'cx', 'mcx'])
        target_qubits = random.sample(range(n_qubits), k=random.randint(1, n_qubits))  

        if gate_type == 'x':
            circuit.x(target_qubits[0])
        
        elif gate_type == 'h':
            circuit.h(target_qubits[0])
        
        elif gate_type == 'ry':
            theta = np.round(random.uniform(0, 2 * np.pi), precision)  
            circuit.ry(theta, target_qubits[0])
        
        elif gate_type == 'rz':
            theta = np.round(random.uniform(0, 2 * np.pi), precision)  
            circuit.rz(theta, target_qubits[0])
        
        elif gate_type == 'cx' and len(target_qubits) > 1:
            circuit.cx(target_qubits[0], target_qubits[1])
        
        elif gate_type == 'mcx' and len(target_qubits) > 1:
            # control_qubits = target_qubits[:-1]
            # target_qubit = target_qubits[-1]
            """
                TODO:
                For now, only implement mcx to act on the last qubit:
            """
            circuit.mcx(list(range(n_qubits-1)), n_qubits-1)
    
    return circuit

def grover_HEA_ansatz(depth, n_qubits, precision, input_state, random_choices, circuit=None, only_grover=False):
    input_state_str = get_initial_state_from_circuit(input_state)
    ansatz_choices = [np.random.choice(random_choices) for _ in range(depth)]
    print("ansatz order:", ansatz_choices)
    params = []
    if circuit == None or only_grover:
        # When only implementing grover, the quantum circuit should be re-initialized
        circuit = QuantumCircuit(n_qubits)
        
    for i in range(depth):
        ansatz_choice = ansatz_choices[i]
        
        if type(input_state_str) != list:
            input_state_str = [input_state_str]
            
        if ansatz_choice == 'Grover':
            iterations = 1
            if only_grover:
                iterations = calculate_grover_iterations(n_qubits, num_target=1)
                print("target state: ", input_state_str)
                print(f"only grover, the iteration nums should be calculated as {iterations}")
                
            circuit = grover_ansatz(n_qubits=n_qubits, 
                          target_states=input_state_str, 
                          iterations=iterations,
                          circuit=circuit)
            
        elif ansatz_choice == "HEA":
            circuit, params = hea_ansatz(num_qubits=n_qubits, 
                                         params=params,
                                         depth=1, 
                                         circuit=circuit,
                                         idx=i,
                                         )
        
        elif ansatz_choice == "Random":
            max_operations = 20 # equal to the number of operations per iteration in grover search
            circuit = random_ansatz(n_qubits, 
                                    max_operations, 
                                    precision, 
                                    circuit=circuit)
            
        elif ansatz_choice == "QAOA":
            circuit, params = qaoa_ansatz(num_qubits=n_qubits, 
                                         params=params,
                                         depth=1, 
                                         circuit=circuit,
                                         idx=i,
                                         )
        elif ansatz_choice == None:
            continue
    return circuit, params, input_state_str