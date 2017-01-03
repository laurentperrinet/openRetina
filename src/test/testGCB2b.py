import GCB2 as comm

b=comm.GCB_REP_REQ(
    req_ip=['localhost'],
    req_port=['6665'],
    #rep_port=['6666'],
    verbose=True)
b.REQ_array()
