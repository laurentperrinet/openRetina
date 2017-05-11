import GCB2 as comm

c=comm.GCB_REP_REQ(req_ip=['localhost'],
    req_port=['6666'],
    verbose=True)
c.REQ()
