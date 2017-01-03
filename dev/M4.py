from Monitor import monitor
import time
import cv2

T_SIM=120
M1=monitor(T_SIM='60',
    input_ip=['localhost'],
    input_port=['6665'],
    mode_comm='RepReq')
i=0
task_delay=list()
start=time.time()
while (time.time() - start) < T_SIM :
    M1.REQ_array()
     ###latency block
    a=round(M1.REQ_latency(),2)
    if i>4:
        average=round(sum(M1._delay_req[4:])/len(M1._delay_req[4:]),2)
        maxi=round(max(M1._delay_req[4:]),2)
        print("--- REQ instant --- : {0} ms  --- REQ max --- : {1} ms , --- REQ avg --- {2} ms".format(a,maxi,average))
    start=time.time()
    M1.GUI1_b()
    end=round((time.time()-start)*1000,2)
    task_delay.append(end)
    average=round(sum(task_delay)/len(task_delay),2)
    maxi=round(max(task_delay),2)
    print("--- TASK instant --- : {0} ms  --- TASK max --- : {1} ms , --- TASK avg --- {2} ms".format(end,maxi,average))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i=i+1
