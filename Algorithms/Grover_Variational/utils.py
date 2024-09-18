import qiskit.qpy as qpy
import numpy as np
from qiskit.quantum_info import Statevector

def export_circuit_to_qasm(circuit, filename):
    decomposed_circuit = circuit.decompose()
    qasm_str = decomposed_circuit.qasm()  
    with open(filename, "w") as f:  
        f.write(qasm_str)
        
def export_circuit_to_qpy(circuit, filename):
    with open(filename, 'wb') as file:
        qpy.dump(circuit, file)
        
def load_circuit_from_qpy(filename):
    with open(filename, 'rb') as file:
        circuit = qpy.load(file)[0]
    return circuit

def extract_after_third_newline(s):
    first_newline = s.find('\n')
    second_newline = s.find('\n', first_newline + 1)
    third_newline = s.find('\n', second_newline + 1)
    if third_newline != -1:
        return s[third_newline + 1:]
    else:
        return ""
    
def truncate_statevector(statevector, precision):
    truncated = np.round(statevector.data, precision)
    return Statevector(truncated)