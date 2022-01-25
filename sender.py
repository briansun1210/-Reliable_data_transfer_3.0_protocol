from socket import * 
import datetime #this is for the date time
import signal #use for stoping server 
import os #get file length
import sys
import time # for sleep
import errno # for handle error from settimeout function 
from checksum import get_checksum
from checksum import checksum_verifier
serverName = 'gaia.cs.umass.edu'
serverPort = 20000

connection_id = sys.argv[1]
loss_rate = sys.argv[2]
corrupt_rate = sys.argv[3]
max_delay = sys.argv[4]
transmission_timeout = float(sys.argv[5])

#defualt variable
gaiaMessage = '' #this is for receive the message from server
# message = "HELLO S 0.0 0.0 0 0001" #default, send message to server said this is sender
message = "HELLO S " + loss_rate + ' ' + corrupt_rate + ' ' + max_delay + ' ' + connection_id

signal.signal(signal.SIGINT, signal.SIG_DFL) #stop server with control-c
clientSocket = socket(AF_INET, SOCK_STREAM) #setup socket
clientSocket.connect((serverName, serverPort)) #connect server

#after connection to the server do...
print('brian sun ',datetime.datetime.now()) #print name, date, time after connect to server
f = open("declaration.txt", "r") #read the file
clientSocket.send(message.encode()) #send the message to the server


while(gaiaMessage == '' or gaiaMessage == 'WAITING'): #waiting for gaiaMessage while receive nothing or WAITING message
    gaiaMessage = clientSocket.recv(1024).decode()
    # print(gaiaMessage)

    if(gaiaMessage.find("OK") != -1): #check is server return "OK" message
        print(datetime.datetime.now(), " channel has been established")


#start to open the text file and send message
f = open("declaration.txt", "r")
fileLength = os.stat('declaration.txt').st_size #get the length of the file

#default checksum and ack value and checksum200 for 200 bytes
checksum = '00000'
ack = '0'
checksum200 = 0

sent_total = 0
received_total = 0
corrupted_message = 0
timeout = 0


# for i in range(int(fileLength / 20) + 1):
for i in range(10):
    check = True
    message = f.read(20)
    if(i % 2 == 0): #the sequen number, first packet always start with 0 and then 1 and 0 so on
        seq = '0'
    else:
        seq = '1'
    
    prePacket = seq + ' ' + ack + ' ' + "{:<20}".format(message) + ' ' + checksum #make pre packet to get the checksum
    checksum = get_checksum(prePacket)
    checksum200 += int(get_checksum(prePacket[4:29])) #4:29 not 4:24 becasue my checksum algorithm will ignore the last 5 bytes

    packet = seq + ' ' + ack + ' ' + "{:<20}".format(message) + ' ' + checksum #prepare packet

    # clientSocket.send(packet.encode())
    while(check):
        # clientSocket.send(packet.encode())
        clientSocket.send(bytes(packet, "utf-8"))
        clientSocket.settimeout(transmission_timeout) #*******************************************************************************************
        # print('set time send: ', i , len(packet))
        sent_total += 1

        try:
            msg = clientSocket.recv(1024).decode()
            received_total += 1
            # print('msg:' + msg, len(msg))
            # print(msg[2] + seq) #*************************************************
            if not msg:               
                print('error from server')
                break
            else:
                if(checksum_verifier(msg) == False): #if the checksum is wronge send the previous package again
                    # print('bad send again', len(msg))
                    corrupted_message += 1
                elif(msg == ''):                     #if the msg is emoty send the previous package again
                    print('msg empty')
                elif(msg[2] == seq):                 #if the ack number is correct, send next package
                    # print(msg + ' good')
                    check = False
                elif(msg != '' and msg[2] != seq):
                    # print('ack not correct')
                    corrupted_message += 1

        except error as e:
            if e.args[0] == errno.EWOULDBLOCK: 
                print ('EWOULDBLOCK')
            else:
                # print('file loss resend:', len(packet))
                # clientSocket.send(packet.encode())
                clientSocket.send(bytes(packet, "utf-8"))
                # print(packet)
                sent_total += 1
                timeout += 1


print('name: BrianSun') 
print('date and time: ', datetime.datetime.now())
print('checksum: ', checksum200)
print('sent total: ', sent_total)
print('receive total: ', received_total)
print('corrupted message: ', corrupted_message)
print('number of timout: ', timeout)


clientSocket.close()
f.close()



