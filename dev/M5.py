from Monitor import monitor
import time
import cv2
import numpy as np

T_SIM=120
M1=monitor(T_SIM='60',
    input_ip=['localhost'],
    input_port=['6665'],
    mode_comm='RepReq',
    verbose=True)

task_delay=list()
start=time.time()
while (time.time() - start) < T_SIM :
    M1.REQ_array()
    #print("dans la fonction monitor")
    #print(M1._data.shape)
    #print(M1._data[63,:,0])
    #print(M1._data[63,:,-1])
    #print(np.mean(M1._data[:,:,1]))
    #print("le type de la matrice entrante est : {0}".format(M1._data.dtype))

    start_task=time.time()
    M1.GUI1_b()
    task_delay.append(round((time.time()-start_task)*1000,2))
    M1.display_task_delay(task_delay)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
