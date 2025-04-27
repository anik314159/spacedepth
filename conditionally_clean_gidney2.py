all_qubits = []
conditionally_clean_ancillae = [-1]    
import math
free_qubits = [ qubits for qubits in range(0,32) ]
# free_qubits.pop(0)
# free_qubits.pop(0)
def generate_toff_pairs_in_a_row(control_size,start_num,borrow,free_qubits,conditionally_clean_ancillae):
    
    #generating conditionally clen ancillae
    last_anc = []
    control_qubits = []
    result_qubit = -1
    temp = start_num
    while temp != 0:
        print(temp,borrow)
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

            if conditionally_clean_ancillae[0] == -1:
                print(f"qc.ccx(q[{free_qubits[0]}],q[{free_qubits[1]}],anc[0])")
            else:
                print(f"qc.ccx(q[{free_qubits[0]}],q[{free_qubits[1]}],q[{conditionally_clean_ancillae[0]}])")
            
            result_qubit = conditionally_clean_ancillae[0]

            last_anc.append(conditionally_clean_ancillae.pop(0))
            # print(last_anc)

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
        free_qubits = last_anc + free_qubits 
        # print(free_qubits)
        last_anc=[]
     
        temp = temp//2
        

    conditionally_clean_ancillae = control_qubits
    
    # print(result_qubit)
    return conditionally_clean_ancillae,free_qubits[1:],result_qubit
        
# free_qubits = free_qubits[19:32]
# conditionally_clean_ancillae = [18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3]
# print(free_qubits)
# print(generate_toff_pairs_in_a_row(32,12,1,free_qubits,conditionally_clean_ancillae))

def create_circuit(control_size):
    print(f"""from qiskit import QuantumRegister, QuantumCircuit

# Define registers
q = QuantumRegister({control_size}, 'q')
anc = QuantumRegister(2, 'anc')
target = QuantumRegister(1, 'target')

# Create the circuit
qc = QuantumCircuit(target,anc,q)""")
    free_qubits = [i for i in range(0,control_size)]
    conditionally_clean_ancillae = [-1]
    start_num = 2
    borrow = 0
    cnt = 0
    result_indices=[]
    # while(conditionally_clean_ancillae[0] != control_size -1)
    result_qubit = -1
    # for i in range(math.ceil(math.log2(control_size))):
    # while(conditionally_clean_ancillae[0] != control_size -1):
    while(len(conditionally_clean_ancillae)>0):
        if (len(free_qubits) == 1):
            result_indices.append(free_qubits[0])
            # cnt +=1
            # print(free_qubits)
            break        
        conditionally_clean_ancillae,free_qubits,result_qubit= generate_toff_pairs_in_a_row(control_size,start_num,borrow,free_qubits,conditionally_clean_ancillae)
        result_indices.append(result_qubit)

        # conditionally_clean_ancillae = sorted(conditionally_clean_ancillae,reverse=True)
        start_num = min(len(conditionally_clean_ancillae),len(free_qubits))

        if (len(conditionally_clean_ancillae) < len(free_qubits)):
            borrow = 1
        else:
            borrow = 0
        print("qc.barrier()")
 
        for k in conditionally_clean_ancillae:
            if conditionally_clean_ancillae[0] != control_size -1 :
                print(f"qc.x(q[{k}])")
        print("qc.barrier()")
        # print(conditionally_clean_ancillae)
        # print(free_qubits)
        # print(len(conditionally_clean_ancillae),len(free_qubits))
        # print(start_num)
        # print(borrow)
        # borrow = 1 
        # if (start_num == len(free_qubits) and start_num % 2 == 1):
        #     start_num = start_num -1
        #     borrow = 1
            # print(start_num)
    list_str=""
    for ele in result_indices:
        if ele == -1:
            list_str += "anc[0],"
            continue
        list_str += "q["+str(ele)+"],"
    print(f"qc.mcx([{list_str[:-1]}],target)")
    print("""latex_code = qc.draw(output='latex_source')
# Write to .tex file
with open("quantum_circuit.tex", "w") as f:    
    f.write(latex_code)
    """)    
    print(result_indices)
    
    

create_circuit(16)