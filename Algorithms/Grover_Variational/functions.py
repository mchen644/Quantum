from qiskit_aer import Aer
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
import random
import math
from qiskit.circuit import QuantumCircuit
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit
import re

def simulate_circuit(circuit):
    backend = Aer.get_backend('statevector_simulator')
    transpiled_circuit = transpile(circuit, backend)
    result = backend.run(transpiled_circuit).result()
    statevector = result.get_statevector()
    return statevector

def calculate_expectation_value(statevector, hamiltonian):
    operator = Operator(hamiltonian)
    expectation_value = np.real(statevector.expectation_value(operator))
    return expectation_value

def create_random_hamiltonian(num_qubits):
    hamiltonian = np.random.rand(2**num_qubits, 2**num_qubits) + 1j * np.random.rand(2**num_qubits, 2**num_qubits)
    hamiltonian = 0.5 * (hamiltonian + hamiltonian.T) 
    return hamiltonian

def apply_variational_angles(circuit, params, precision):
    angle_values = {param: np.round(random.uniform(0, 2 * np.pi), precision) for param in params}
    bound_circuit = circuit.assign_parameters(angle_values)
    return bound_circuit

def calculate_grover_iterations(n_qubit, num_target):
    return math.floor(np.pi / 4 * np.sqrt(2**n_qubit/num_target))

def get_initial_state_from_circuit(circuit: QuantumCircuit) -> str:
    """
    return the initial state;
    if the initial state is in superposition, then return 'Superposition'
    """
    num_qubits = circuit.num_qubits
    initial_state = ['0'] * num_qubits 
    for instr, qargs, _ in circuit.data:
        if instr.name in ['h', 'ry', 'rx']:
            return 'Superposition'
        
        if instr.name == 'x':
            qubit_index = qargs[0]._index
            initial_state[qubit_index] = '1'

    return ''.join(initial_state)

def simplify_qasm(qasm_string):
    pattern = r'qubit\[\d+\] q;\n(.*)'
    match = re.search(pattern, qasm_string, re.DOTALL)

    if match:
        result = match.group(1)
    else:
        print("No match str")
    return result

def create_random_initial_state(num_qubits, precision, only_grover):
    circuit = QuantumCircuit(num_qubits)
    
    for qubit in range(num_qubits):
        if np.random.choice([True, False]):
            circuit.x(qubit) 
        
        if only_grover:
            continue
        
        if np.random.choice([True, False]):
            circuit.h(qubit) 
            
        elif np.random.choice([True, False]):
            theta = np.round(np.random.uniform(0, 2 * np.pi), precision) 
            circuit.ry(theta, qubit) 

    return circuit

def is_superposition_from_circuit(circuit: QuantumCircuit) -> bool:
    for instr, _, _ in circuit.data:
        if instr.name in ['h', 'ry', 'rx']:
            return True
    return False
