import numpy as np
from numpy import pi
# importing Qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram, plot_bloch_multivector
import time
import random
import os
import pickle

def qft_rotations(circuit, n):
    """Performs qft on the first n qubits in circuit (without swaps)"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, n)
    
def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

def encode_state(qc, state, num_qubits):
    # Convert the state to its binary representation
    binary_state = bin(state)[2:].zfill(num_qubits)  # convert state to binary and fill leading 0s
    
    # Apply X gates based on the binary representation
    for i, bit in enumerate(reversed(binary_state)):  # reverse to match qubit order (q0 as LSB)
        if bit == '1':
            qc.x(i)

if __name__ == '__main__':
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    st = time.time()
    
    num_qubits = 5
    num_samples = 1
    
    for _ in range(num_samples):
        qc = QuantumCircuit(num_qubits)
        input_state = ''.join(random.choice('01') for _ in range(num_qubits))
        input_state_decimal = int(input_state, 2)
        data = {}
        encode_state(qc, input_state_decimal, num_qubits)
        qc.draw('mpl')

        sim = Aer.get_backend("aer_simulator")
        qc_init = qc.copy()
        qc_init.save_statevector()
        statevector = sim.run(qc_init).result().get_statevector()
        
        plot_bloch_multivector(statevector)

        qft(qc,num_qubits)
        qc.draw('mpl')
        qc.save_statevector()
        statevector = sim.run(qc).result().get_statevector()
        print(statevector)
        # print(list(np.asarray(statevector)))
        data[input_state] = list(np.asarray(statevector))
        print(data)
        print("Cost time:", time.time() - st)
        file_name = f"{num_qubits}"+ "_" + f"{input_state}" + ".pkl"
        file_path = os.path.join(data_dir, file_name)
        with open(file_path, 'wb') as file:
            pickle.dump(data, file)
        
    
    # plot_bloch_multivector(statevector)
    # counts = sim.run(qc_init).result().get_counts()
    # plot_histogram(counts)