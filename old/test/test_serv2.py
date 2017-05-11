import GCB

comm_worker=GCB.GCB(
    input_ip=['localhost'],
    input_port=['5556'],
    output_port=['5558'])

while True:
    comm_worker.pull(
        index=[0]
    )
    comm_worker.push(
        index=[0]
        )
