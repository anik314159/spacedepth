from itertools import combinations
import re
def binary_to_anf(binary_string):
    assert len(binary_string) == 32, "Binary string must be 32 bits long."
    
    variables = ['x1', 'x2', 'x3', 'x4', 'x5']
    terms = []
    if binary_str[0] == '1':
        terms[0] = "1"
    
    index = 1
    
    # Generate monomials from single vars to x1x2x3x4x5
    for r in range(1, 6):  
        for combo in combinations(variables, r):
            term = "".join(combo)
            if binary_string[index] == '1':
                terms.append(term)
            index += 1

    return terms if terms else 0 
'''
Function to generate projectq code from terms,
Only supports till mcx decompositions cannot generate toffoli or T gated circuits
'''

def write_projectq(file,terms):
    with open(file,"w") as f:
        f.write("""
from projectq.backends import CircuitDrawer
from collections import defaultdict
from projectq import MainEngine
from projectq.ops import H, X, Measure, Toffoli,CNOT
from projectq.backends import ClassicalSimulator,ResourceCounter

from projectq.cengines import BasicEngine\n""")
        f.write("from projectq import MainEngine\n")
        f.write("from projectq.ops import Swap, All, Measure\n\n")
        
        f.write("""
class DepthTracker(BasicEngine):
    def __init__(self):
        super().__init__()
        self.qubit_depth = defaultdict(int)  # Track depth per qubit
        self.max_depth = 0  # Global circuit depth

    def receive(self, command_list):
        
        for command in command_list:
            # Extract qubits used in this operation
            involved_qubits = [qb.id for qr in command.all_qubits for qb in qr]

            # Skip allocate/deallocate commands, but process others
            if command.gate == "Allocate" or command.gate == "Deallocate":
                continue

            # Determine the layer in which this operation will execute
            current_layer = max(self.qubit_depth[q] for q in involved_qubits) + 1

            # Update depth for each involved qubit
            for q in involved_qubits:
                self.qubit_depth[q] = current_layer

            # Update global max depth
            self.max_depth = max(self.max_depth, current_layer)

        # Forward commands to the next engine
        self.next_engine.receive(command_list)

    def get_depth(self):
        return self.max_depth
        \n\n""")
        #Allocation code
        for i in range(5):
            f.write(f"x{i+1} = eng.allocate_qubit()\n")
        for index,term in enumerate(terms):
            term_len = int(len(term)/2 if term != "1" else 0) 
            if term_len > 1:
                f.write(f"q{index} = eng.allocate_qureg({term_len})\n")
            
        f.write(f"result = eng.allocate_qubit()\n")
        #CNOT copying (Poly-n)
        for index,term in enumerate(terms):
            var_names = re.findall(r"x\d",term)
            term_len = len(var_names)

            if term_len > 1:
                cnt = 0
                for name in var_names:
                    f.write(f"CNOT | ({name},q{index}[{cnt}])\n")
                    cnt += 1

        #Toffoli Mapping
        for index,term in enumerate(terms):
            term_len = int(len(term)/2 if term != "1" else 0)            
            # f.write(f"q{index} = eng.allocate_qureg({term_len})\n")

            if term_len == 1: 
                f.write(f"CNOT | ({term},result)\n")
            elif term_len > 1:
                f.write(f"C(X,{term_len}) | (q{index},result)\n")
            else:
                f.write(f"X | (result)\n")
'''
Code for decomoposion of a Multi controlled toffoli into Toffoli gates

Decomposition is consists of n-2 ancillae which are expected to be appended
to the control qubits -

For example:
    if there is an mcx gate corresponding to the term q1 = x1x2x3
    there will be a total 3 + (3-2) + 1 = 5 qubits used the ancillae 
    are assumed to be appended after the first 3 terms

arguments:

control_size: The size of qubits in control
control_qubit: The name of the term used "q1", "q2" etc.
result_index: The index of the result array used for the term 
tgate: switch to indicate tgate synthesis for each ccx gate
'''
             
def decompose_n_toff_to_toff(control_size,control_qubit,result_index,tgate):
    cnt = 0
    # while(control_size != 0):
    lines = []
    i = 0
    for i in range(0,2*control_size-4 ,2):
        
        if tgate == True:
            for line in decompose_n_toff_to_t_gate(f"{control_qubit}[{i}]",f"{control_qubit}[{i+1}]",f"{control_qubit}[{control_size + cnt}]"):
                lines.append(line)
        else:
            lines.append(f"qc.ccx({control_qubit}[{i}],{control_qubit}[{i+1}],{control_qubit}[{control_size + cnt}])\n")

        cnt += 1
    if tgate == True:
        for line in decompose_n_toff_to_t_gate(f"{control_qubit}[{i+2}]",f"{control_qubit}[{i+3}]",f"result[{result_index}]"):
            lines.append(line)
    else:
        lines.append(f"qc.ccx({control_qubit}[{i+2}],{control_qubit}[{i+3}],result[{result_index}])\n")
    

    return lines
bus_cnt = 0


'''
Code to decompose a Toffoli gate into T gate , Decomposition based on Jaques et.al
,Eurocrypt 2020, 

arg1 - First input to Toffoli gate
arg2 - Second input to Toffoli gate
arg3 - Output line of Toffoli gate
'''
def decompose_n_toff_to_t_gate(arg1,arg2,arg3):
    # cnt = 0
    global bus_cnt
    lines = []

    lines.append(f"qc.h({arg3})\n")
    lines.append(f"qc.cx({arg2},bus0[{bus_cnt}])\n")
    lines.append(f"qc.cx({arg3},{arg1})\n")
    lines.append(f"qc.cx({arg3},{arg2})\n")
    lines.append(f"qc.cx({arg1},{arg2})\n")

    lines.append(f"qc.tdg({arg1})\n")
    lines.append(f"qc.tdg({arg2})\n")
    lines.append(f"qc.t({arg3})\n")
    lines.append(f"qc.t(bus0[{bus_cnt}])\n")

    lines.append(f"qc.cx({arg1},{arg2})\n")
    lines.append(f"qc.cx({arg3},{arg2})\n")
    lines.append(f"qc.cx({arg3},{arg1})\n")
    lines.append(f"qc.cx({arg2},bus0[{bus_cnt}])\n")
    lines.append(f"qc.h({arg3})\n")
    lines.append(f"qc.s({arg3})\n")
    # lines.append(f"qc.barrier()\n")

    bus_cnt += 1
    # return lines

    # # while(control_size != 0):
    # lines = []
    # for i in range(0,2*control_size-4 ,2):
        
    #     lines.append(f"qc.ccx({control_qubit}[{i}],{control_qubit}[{i+1}],{control_qubit}[{control_size + cnt}])\n")
    #     lines.append(f"qc.h({control_qubit}[{control_size + cnt}])\n")
    #     cnt += 1
    # lines.append(f"qc.ccx({control_qubit}[{i+2}],{control_qubit}[{i+3}],result[{result_index}])\n")
    return lines 

def write_qiskit(file,terms,n,tgate=False):
    with open(file,"w") as f:
        qreg_list = []
        #Allocation code
        f.write("""from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, transpile, assemble, execute
from qiskit.visualization import circuit_drawer\n""")
        for i in range(n):
            f.write(f"x{i+1} = QuantumRegister(1,'x{i+1}')\n")
            qreg_list.append(f"x{i+1}")
        for index,term in enumerate(terms):
            term_len = int(len(term)/2 if term != "1" else 0) 
            # if term_len == 2:
            #     f.write(f"q{index} = QuantumRegister({term_len},'q{index}')\n")
            #     qreg_list.append(f"q{index}")

            if term_len > 1:
                f.write(f"q{index} = QuantumRegister({2*term_len-2},'q{index}')\n")
                qreg_list.append(f"q{index}")
        if tgate == True:
            f.write(f"bus0 = QuantumRegister(10,'bus0')\n")
            qreg_list.append("bus0")

        f.write(f"result = QuantumRegister({len(terms)+1},'result')\n")
        
        qreg_str = ""
        qreg_list.append("result")
        for reg in qreg_list:
            if reg != "result":
                qreg_str += reg + ","
            else:
                qreg_str += reg
        f.write(f"qc = QuantumCircuit({qreg_str})\n")  
        #CNOT copying (Poly-n)
        for index,term in enumerate(terms):
            var_names = re.findall(r"x\d+",term)
            term_len = len(var_names)
            print(var_names)
            # if term_len > 1 and term_len != n:
            if term_len > 1:
                # f.write("qc.barrier()\n")
                cnt = 0
                for name in var_names:
                    f.write(f"qc.cx({name},q{index}[{cnt}])\n")
                    cnt += 1
                f.write("qc.barrier()\n")

        #Toffoli Mapping
        for index,term in enumerate(terms):
            # f.write("qc.barrier()\n")

            term_len = int(len(term)/2 if term != "1" else 0)            
            # f.write(f"q{index} = eng.allocate_qureg({term_len})\n")

            if term_len == 1: 
                f.write(f"qc.cx({term},result[{index}])\n")
            # elif term_len == 5:
            #     f.write(f"qc.mcx([x1,x2,x3,x4,x5],result[{index}])\n")
            elif term_len == 2:
                if tgate == True:
                    for line in decompose_n_toff_to_t_gate(f"q{index}[0]",f"q{index}[1]",f"result[{index}]"):
                        f.write(line)
                else:
                    f.write(f'qc.ccx(q{index}[0],q{index}[1],result[{index}])\n')
            elif term_len > 2:
                # f.write(f"qc.mcx(q{index},result[{index}])\n")

                for line in decompose_n_toff_to_toff(term_len,f"q{index}",index,tgate):
                    f.write(line)
            else:
                f.write(f"qc.x(result[{index}])\n")

        #result_mapping

        for i in range(len(terms)):
            f.write(f"qc.cx(result[{i}],result[{len(terms)}])\n")
        
        f.write("""latex_code = circuit_drawer(qc, output='latex_source')
with open("circuit.tex", "w") as f:
    f.write(latex_code)
with open("circuit.qasm", "w") as f:
    f.write(qc.qasm())""")
                           

             


binary_str = "00000000000000000000000000000001"
# binary_str = str(input("Please Enter a 32 bit expression"))
anf_expression = binary_to_anf(binary_str)
print(anf_expression)
anf_str = ""
n = 16
for i in range (1,n+1):
    anf_str += "x"+str(i)
anf_expression = [anf_str]
print(anf_expression)
write_qiskit("./outfile.py",anf_expression,n,tgate=False)

