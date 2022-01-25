# -Reliable_data_transfer_3.0_protocol
Sender and receiver will be communicating over TCP sockets, over a “live” Internet. 

Run sender with: `python sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout>`

Run receiver with: `python receiver.py <connection_id> <loss_rate> <corrupt_rate> <max_delay>`

<loss_rate> <corrupt_rate> are float values in the range [0.0, 1.0]. <loss rate> and 
<corrupt rate> are the probabilities that a message will be lost or corrupted, 
respectively. 
