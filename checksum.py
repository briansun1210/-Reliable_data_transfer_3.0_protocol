# msg = 'That was the time fo'
# msg2 = '12345'

def get_checksum(msg):
    read = len(msg) - 5 #get everything except the last 5 digite
 
    byte = msg[:read].encode("utf-8")
    s = 0

    for i in range(0, len(byte), 1):

        s += byte[i]  #get the sum of Dec number from the message

    return format(s, '05d')


def checksum_verifier(msg):
    check = True
    expected_packet_length = 30

    if len(msg) < expected_packet_length:
        check = False

    if(get_checksum(msg) == msg[-5:]):
        check = True
    else:
        check = False

    
    return check