from VisionSensor import VisionSensor
import GCB2 as comm
import time
## Defining the communicating port
T_SIM=40;


Camera=VisionSensor(T_SIM='40',
                    #input_ip =['localhost'],
                    #input_port = ['7000'],
                    output_port=['6666'],
                    cam_type="PiCam",
                    mode='RGB',
                    mode_comm='RepReq',
                    sync=False,
                    verbose=True)

start=time.time()
task_delay=list()
i=0
while time.time()-start<T_SIM:

    start=time.time()
    ### Delay calculation for main task
    Camera._data=Camera.acquire_frame()
    task_delay.append(round((time.time()-start)*1000,2))
    Camera.display_task_delay(task_delay)

    Camera.REP_array(Camera._data)
