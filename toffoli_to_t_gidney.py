from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate, QuantumRegister
from qiskit.circuit.library import CCXGate

def decompose_toffoli(qc, controls, target):
    """Add the T-gate based decomposition of Toffoli to the circuit."""
    a, b = controls
    c = target
    qc.barrier()
    qc.t(target)
    qc.h(target)
    qc.cx(a,target)
    qc.cx(b,target)
    qc.cx(target,b)
    qc.cx(target,a)
    qc.barrier()
    qc.tdg(a)
    qc.tdg(b)
    qc.t(c)
    qc.barrier()
    qc.cx(target,a)
    qc.cx(target,b)
    qc.h(target)
    qc.s(target)
    qc.barrier()

def replace_toffolis(qc):
    """Replace all Toffoli gates with T-gate decompositions."""
    new_qc = QuantumCircuit(*qc.qregs)  # Preserve registers correctly
    
    for instr, qargs, cargs in qc.data:
        if isinstance(instr, CCXGate):
            controls = [qargs[0], qargs[1]]
            target = qargs[2]
            decompose_toffoli(new_qc, controls, target)
        else:
            new_qc.append(instr, qargs, cargs)
    
    return new_qc

# Load your circuit
qc = QuantumCircuit.from_qasm_file("./quantum_circ.qasm")  # Replace with your file path
print("Original Circuit:")
print(qc)

# Replace Toffolis
new_qc = replace_toffolis(qc)
print("\nCircuit After Toffoli Replacement:")
print(new_qc)

# Save the new circuit if needed
new_qc.qasm(filename="new_quantum_circuit.qasm")