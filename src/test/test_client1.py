import GCB

comm_client=GCB.GCB(
    input_ip=['localhost'],
    input_port=['5556']
    )

while True:
    comm_client.pull(
        index=[0]
        )
