all_qubits = []
conditionally_clean_ancillae = [-1]    
import math
free_qubits = [ qubits for qubits in range(0,32) ]
# free_qubits.pop(0)
# free_qubits.pop(0)

def qubit_str(idx):
    if idx < 0:
        return f"anc[{-(idx) - 1}]"
    else:
        return f"q[{idx}]"

def generate_toff_pairs_in_a_row(control_size,start_num,borrow,free_qubits,num_ancilla,conditionally_clean_ancillae):
    
    #generating conditionally clean ancillae
    last_anc = []
    control_qubits = []
    result_qubit = -1
    temp = start_num
    while temp != 0:
        # print(temp,borrow)
        if (temp % 2 != 0 and borrow == 1):
            temp = temp + borrow
            lim = (temp)//2
            borrow = 0
            # print("flag",lim)
        elif (temp %2 != 0 and borrow == 0):
            borrow = 1
            temp = temp - borrow
            lim = temp //2
        else:
            lim = temp // 2

        for i in range(lim):
            # print(free_qubits)
            if len(conditionally_clean_ancillae) == 0:
                break
            if conditionally_clean_ancillae[0] < 0:
                print(f"qc.ccx({qubit_str(free_qubits[0])}, {qubit_str(free_qubits[1])}, {qubit_str(conditionally_clean_ancillae[0])})")
            else:
                print(f"qc.ccx({qubit_str(free_qubits[0])}, {qubit_str(free_qubits[1])}, {qubit_str(conditionally_clean_ancillae[0])})")            
            result_qubit = conditionally_clean_ancillae[0]
            last_anc.append(conditionally_clean_ancillae.pop(0))
            # print(last_anc)
            print(conditionally_clean_ancillae)
            control_qubits.append(free_qubits.pop(0))
            control_qubits.append(free_qubits.pop(0))
            # print(free_qubits)

        # free_qubits = last_anc + free_qubits      

        # if (temp % 2 != 0 and borrow == 1):
        #     for i in range((temp % 2 + borrow)//2):
        #         # print(free_qubits)
        #         if conditionally_clean_ancillae[0] == -1:
        #             print(f"qc.ccx(q[{free_qubits[0]}],q[{free_qubits[1]}],anc[0])")
        #         else:
        #             print(f"qc.ccx(q[{free_qubits[0]}],q[{free_qubits[1]}],q[{conditionally_clean_ancillae[0]}])")
            
        #         result_qubit = conditionally_clean_ancillae[0]

        #         # last_anc.append(conditionally_clean_ancillae.pop(0))
        #         # print(last_anc)
        #         control_qubits.append(free_qubits.pop(0))
        #         control_qubits.append(free_qubits.pop(0))
        #         free_qubits = [conditionally_clean_ancillae.pop(0)] + free_qubits

        #         borrow = 0
        if last_anc[0:num_ancilla] == [-i for i in range(1,num_ancilla+1)] and num_ancilla > 0:            
            last_anc = last_anc[num_ancilla-1:]
        free_qubits = last_anc + free_qubits 
        # print(free_qubits)
        last_anc=[]
     
        temp = temp//2
        
    print(control_qubits)
    conditionally_clean_ancillae = control_qubits
    
    # print(result_qubit)
    return conditionally_clean_ancillae,free_qubits[1:],result_qubit
        
# free_qubits = free_qubits[19:32]
# conditionally_clean_ancillae = [18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3]
# print(free_qubits)
# print(generate_toff_pairs_in_a_row(32,12,1,free_qubits,conditionally_clean_ancillae))

def create_sub_circuit(control_size,num_ancilla,free_qubits,conditionally_clean_ancillae):
#     print(f"""from qiskit import QuantumRegister, QuantumCircuit

# # Define registers
# q = QuantumRegister({control_size}, 'q')
# anc = QuantumRegister({num_ancilla}, 'anc')
# target = QuantumRegister(1, 'target')

# # Create the circuit
# qc = QuantumCircuit(target,anc,q)""")
    # free_qubits = [i for i in range(0,control_size)]
    # conditionally_clean_ancillae = [-i for i in range(1,num_ancilla+1)] 
    #give as input to higher function 
    num_ancilla = num_ancilla
    start_num = 2*num_ancilla
    borrow = 0
    cnt = 0
    extra_ancilla = conditionally_clean_ancillae
    result_indices = []
    # while(conditionally_clean_ancillae[0] != control_size -1)
    result_qubit = -1
    while(len(conditionally_clean_ancillae) >= 1):
        if (len(free_qubits) == 1):
            result_indices.append(free_qubits[0])
            # cnt +=1
            # print(free_qubits)
            break        
        conditionally_clean_ancillae,free_qubits,result_qubit= generate_toff_pairs_in_a_row(control_size,start_num,borrow,free_qubits,num_ancilla,conditionally_clean_ancillae)
        result_indices.append(result_qubit)
        num_ancilla = 0
        
        start_num = min(len(conditionally_clean_ancillae),len(free_qubits))

        if (len(conditionally_clean_ancillae) < len(free_qubits)):
            borrow = 1
        else:
            borrow = 0

        if len(conditionally_clean_ancillae) >= 1:
            print("qc.barrier()")
            for k in conditionally_clean_ancillae:            
                print(f"qc.x({qubit_str(k)})")
            print("qc.barrier()")
        
    list_str=""
    result_indices = set(extra_ancilla[:num_ancilla-1] + result_indices) 
    print(result_indices)
    # for ele in result_indices:
    #     if ele < 0:
    #         list_str += f"anc[{(-ele) - 1}],"
    #         continue
    #     list_str += "q["+str(ele)+"],"
    # print(f"qc.mcx([{list_str[:-1]}],target)")
#     print("""latex_code = qc.draw(output='latex_source')
# # Write to .tex file
# with open("quantum_circuit_ancilla.tex", "w") as f:    
#     f.write(latex_code)
#     """)    
    print(result_indices)
    return result_indices



def create_circuit(control_size,num_ancilla):
    m1 = 0
    m2 = 0
    if num_ancilla < 4:
        m2 = 1
        m1 = num_ancilla - m2        
    else:
        m2 = 2
        m1 = num_ancilla - m2

    print(f"""from qiskit import QuantumRegister, QuantumCircuit

# Define registers
q = QuantumRegister({control_size}, 'q')
anc = QuantumRegister({num_ancilla}, 'anc')
target = QuantumRegister(1, 'target')

# Create the circuit
qc = QuantumCircuit(target,anc,q)""")
    free_qubits = [i for i in range(0,control_size)]
    conditionally_clean_ancillae = [-i for i in range(1,m1+1)] 

    result_indices = create_sub_circuit(control_size,m1,free_qubits,conditionally_clean_ancillae)

    free_qubits_n = list(result_indices)
    conditionally_clean_ancillae = [-i for i in range(m1+1,m2+m1+1)]
    #filter out positive values 
    # print("conditional", result_indices)
    result_indices = create_sub_circuit(len(result_indices),m2,free_qubits_n,conditionally_clean_ancillae)
    # print(result_indices)
    print("""latex_code = qc.draw(output='latex_source')
# Write to .tex file
with open("quantum_circuit_ancilla.tex", "w") as f:    
    f.write(latex_code)
    """)    
create_circuit(16,4)
