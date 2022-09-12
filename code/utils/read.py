import os
import sys

os.environ['KMP_DUPLICATE_LIB_OK']='True'
curr_path = os.path.dirname(os.path.abspath(__file__))  # absolute path of current file
parent_path = os.path.dirname(curr_path)  # parent path
sys.path.append(parent_path)  # add path to sys path

import numpy as np

    
    
def read_JSP(Instance_name):
    with open("Input/JSP/" + Instance_name + '.txt') as f:
        if f.read(1) == "#":
            line = f.readline()
        else:
            f.seek(0)
        line = f.readline()
        msg = line.strip().split()[0: 2]
        job_num, machine_num = int(msg[0]), int(msg[1])
        machine_arrangement = np.zeros((job_num, machine_num), dtype=np.int32)
        process_time_matrix = np.zeros((job_num, machine_num), dtype=np.int32)
        for i in range(job_num):
            line = f.readline().strip().split()
            for j in range(0, 2 * machine_num, 2):
                machine_arrangement[i][j // 2] = int(line[j])
                process_time_matrix[i][j // 2] = int(line[j + 1])
        f.close()
    
    Jobs = []
    for i in range(job_num):
        Jobs.append(Job(process_time_matrix[i], machine_arrangement[i], i))
                
    return Jobs



class Job:
    def __init__(self, process_time, machine_arrange, number) -> None:
        self.process_time, self.machine_arrange = process_time, machine_arrange
        self.No = number
        self.cur = 0
        self.startTime = []
        self.endTime = []
        self.done = False
        self.total_process_time = sum(self.process_time)
        
    def reset(self):
        self.cur = 0
        self.startTime.clear()
        self.endTime.clear()
        self.done = False
        self.total_process_time = sum(self.process_time)