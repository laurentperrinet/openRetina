from Monitor import monitor
import time
import cv2

T_SIM=120
M1=monitor(T_SIM='60',input_ip=['localhost'],input_port=['6664'],mode_comm='RepReq')
i=0
start=time.time()
while (time.time() - start) < T_SIM :
    M1.REQ_array()
    a=M1.REQ_latency()
    print("latence instant REQ : {}".format(a))
    if i>4:
        average=sum(M1._delay_req[4:])/len(M1._delay_req[4:])
        maxi=max(M1._delay_req[4:])
        print("le max REQ est {}, la moyenne REQ est {}".format(maxi,average))
    start=time.time()
    M1.GUI1_b()
    print("main task time {} ".format((time.time()-start)*1000))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i=i+1
