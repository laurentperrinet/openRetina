from DoG import DoG

import time
## Defining the communicating port
T_SIM=30;

DoG1=DoG(T_SIM='30',
        input_ip=['localhost'],
        input_port=['6666'],
        output_port=['6665'],
        mode_comm='RepReq')

start=time.time()
i=0
task_delay=list()
while time.time()-start<T_SIM:
    #DoG1.REQ_array_image()
    DoG1.REQ_array()

    #a=round(DoG1.REQ_latency(),2)
    #if i>4:
    #    average=round(sum(DoG1._delay_req[4:])/len(DoG1._delay_req[4:]),2)
    #    maxi=round(max(DoG1._delay_req[4:]),2)
    #    print("--- REQ instant --- : {0} ms  --- REQ max --- : {1} ms , --- REQ avg --- {2} ms".format(a,maxi,average))

    start=time.time()
    DoG1.DoG1_save()
    task_delay.append(round((time.time()-start)*1000,2))
    DoG1.display_task_delay(task_delay)

    DoG1.REP_array(DoG1.output_data)

    #print(rep_array)

    #b=round(DoG1.REP_latency(),2)
    #if i >4:
    #    average=round(sum(DoG1._delay_rep[4:])/len(DoG1._delay_rep[4:]),2)
    #        maxi=round(max(DoG1._delay_rep[4:]),2)
    #    print("--- REP instant --- : {0} ms  --- REP max --- : {1} ms , --- REP avg --- {2} ms".format(b,maxi,average))
    #Camera._data=Camera.acquire_frame()
    #.REP_array(Camera._data)

    i=i+1
'''
DoG1=DoG(T_SIM='60',input_ip=['localhost'],input_port=['6666'],output_port=['6665'])

DoG1.DoG1()
'''
