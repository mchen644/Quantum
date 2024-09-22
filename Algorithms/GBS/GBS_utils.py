import io
import sys

import numpy as np
import strawberryfields as sf
from strawberryfields.ops import Interferometer, Sgate

def gbs_simulation(n_modes=4, squeezing_param=1.0, cutoff_dim=5, seed=None):
    """
    Simulates a Gaussian Boson Sampling circuit and returns the output quantum state.

    Parameters:
    - n_modes (int): Number of modes in the circuit.
    - squeezing_param (float or list): Squeezing parameter(s) for the input squeezed states.
    - cutoff_dim (int): Cutoff dimension for the Fock basis.
    - seed (int or None): Seed for random number generator (for reproducibility).

    Returns:
    - state_vector (ndarray): The output quantum state vector.
    - prog (sf.Program): The Strawberry Fields program representing the circuit.
    """
    if seed is not None:
        np.random.seed(seed)

    if isinstance(squeezing_param, float) or isinstance(squeezing_param, int):
        squeezing_params = [squeezing_param] * n_modes
    elif isinstance(squeezing_param, list) or isinstance(squeezing_param, np.ndarray):
        if len(squeezing_param) != n_modes:
            raise ValueError("Length of squeezing_param list must equal n_modes.")
        squeezing_params = squeezing_param
    else:
        raise TypeError("squeezing_param must be a float, int, list, or ndarray.")

    U = sf.utils.random_interferometer(n_modes)

    prog = sf.Program(n_modes)
    with prog.context as q:
        for i in range(n_modes):
            Sgate(squeezing_params[i]) | q[i]

        Interferometer(U) | q

    eng = sf.Engine("fock", backend_options={"cutoff_dim": cutoff_dim})

    results = eng.run(prog)

    state = results.state

    state_vector = state.ket()

    return state_vector, prog


def capture_circuit_output(prog):
    buffer = io.StringIO()
    sys.stdout = buffer

    prog.compile(compiler="fock").print()

    sys.stdout = sys.__stdout__

    circuit_output = buffer.getvalue()

    return circuit_output

def save_program_and_results(state_vector, prog, n_modes, squeezing_param, cutoff_dim):
    program_dict = {
        "n_modes": n_modes,
        "squeezing_param": squeezing_param,
        "cutoff_dim": cutoff_dim,
        "results": {},
    }

    indices = np.argwhere(np.abs(state_vector) > 1e-6)

    circuit_str = capture_circuit_output(prog)
    program_dict["circuit"] = circuit_str

    for idx in indices:
        amplitude = state_vector[tuple(idx)]

        binary_index = "".join(map(str, idx))

        program_dict["results"][binary_index] = amplitude

    return program_dict

# Print the complex amplitudes
# print("State vector shape:", state_vector.shape)
# print("Non-zero amplitudes and their indices:")
# indices = np.argwhere(np.abs(state_vector) > 1e-6)
# for idx in indices:
#     amplitude = state_vector[tuple(idx)]
#     print(f"Index {tuple(idx)}: Amplitude {amplitude}")


# # Example: Probability of measuring the state |1, 0, 0, 1>
# state_index = (1, 0, 0, 1)
# amplitude = state_vector[state_index]
# probability = np.abs(amplitude) ** 2
# print(f"Probability of measuring state {state_index}: {probability}")
