from Monitor import monitor
import time
import cv2

T_SIM=120
M3=monitor(T_SIM='60',input_ip=['10.0.0.1'],input_port=['6666'],mode_comm='RepReq')

start=time.time()
while (time.time() - start) < T_SIM :
    M3.REQ_array()
    M3.GUI1_b()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
