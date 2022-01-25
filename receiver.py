from socket import * 
import datetime #this is for the date time
import signal #use for stoping server 
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

#defualt variable
gaiaMessage = '' #this is for receive the message from server
#message = "HELLO R 0.5 0.5 2 0001" #default, send message to server said this is receiver
message = "HELLO R " + loss_rate + ' ' + corrupt_rate + ' ' + max_delay + ' ' + connection_id

signal.signal(signal.SIGINT, signal.SIG_DFL) #stop server with control-c
clientSocket = socket(AF_INET, SOCK_STREAM) #setup socket
clientSocket.connect((serverName, serverPort)) #connect server

#after connection to the server do... 
print('brian sun ',datetime.datetime.now()) #print name, date, time after connect to server
clientSocket.send(message.encode())


while(gaiaMessage == '' or gaiaMessage == 'WAITING'): #waiting for gaiaMessage while receive nothing or WAITING message
    gaiaMessage = clientSocket.recv(1024).decode()
    # print(gaiaMessage)

    if(gaiaMessage.find("OK") != -1): #check is server return "OK" message
        print(datetime.datetime.now(), " channel has been established")
        # gaiaMessage = clientSocket.recv(1024).decode()
        # print(gaiaMessage)

#*******************************************************************************************************************************************
count = 0 #this count is to keep in track the sequen number, first packet always start with 1 and then 0 and 1 so on
checksum = ''
correct = 0 #testing
checksum200 = 0
copymsg = '' #check duplicate message

sent_total = 0
received_total = 0
corrupted_message = 0

while (True):
    flag = True #this flag is for checking if the package is correct, is the package is not correct, receiver's expect seq number should not change
    if(count % 2 == 0): #the sequen number, first packet always start with 1 and then 0 and 1 so on
        seq = '0'
    else:
        seq = '1'
   
    
    msg = clientSocket.recv(1024).decode() #get the message from the sender

    if(msg == ''): #if the msg is empty that means no more message from the sender
        # print('empty')
        break

    received_total += 1

    if((msg[0] != seq) and (checksum_verifier(msg) == False)):  #check is the seq and checksum is wroing 
        if(seq == '1'):
            seq = '0'
        else:
            seq = '1'

        preMessage = ' '*2 + seq + ' '*27 
        checksum = get_checksum(preMessage) 
        message = ' '*2 + seq + ' '*22 + checksum
        clientSocket.send(bytes(message, "utf-8"))
        # print('1', len(message))
        sent_total += 1
        corrupted_message += 1
        flag = False

    #check delay, which will have duplicate problem
    elif(msg == copymsg): 
        if(seq == '1'):
            ack = '0'
        elif(seq == '0'):
            ack = '1'
        preMessage = ' '*2 + ack + ' '*27 #prepar the message to send back with specific formate
        checksum = get_checksum(preMessage) #get the checksum 
        message = ' '*2 + ack + ' '*22 + checksum
        clientSocket.send(bytes(message, "utf-8"))
        # print('2', len(message))
        sent_total += 1
        # print('duplicate')
        # print(message)
        flag = False    #keep waiting the expacted seq number, (take the flag away can make the process faster)

    #checksum correct
    elif((checksum_verifier(msg) == True)):  
        copymsg = msg  
        checksum200 += int(get_checksum(msg[4:29])) #get the message bytes(20)  ******4:29******* because my checksum function will ignore the last 5 bytes

        preMessage = ' '*2 + seq + ' '*27 #prepar the message to send back with specific formate
        checksum = get_checksum(preMessage) #get the checksum 
        message = ' '*2 + seq + ' '*22 + checksum
        clientSocket.send(bytes(message, "utf-8"))
        # print('3', len(message))
        sent_total += 1

    #if checksum is wrong, that means the seq number is correct, becasue the previous stament check 
    elif(checksum_verifier(msg) == False):
        if(msg[0] == seq == '1'):
            ack = '0'
        elif(msg[0] == seq == '0'):
            ack = '1'
        preMessage = ' '*2 + ack + ' '*27 #prepar the message to send back with specific formate
        checksum = get_checksum(preMessage) #get the checksum 
        message = ' '*2 + ack + ' '*22 + checksum
        clientSocket.send(bytes(message, "utf-8"))
        # print('4', len(message))
        sent_total += 1
        corrupted_message += 1
        flag = False
    else:
        preMessage = ' '*2 + ack + ' '*27 #prepar the message to send back with specific formate
        checksum = get_checksum(preMessage) #get the checksum 
        message = ' '*2 + ack + ' '*22 + checksum
        clientSocket.send(bytes(message, "utf-8"))
        # print('5', len(message))
        sent_total += 1
        corrupted_message += 1
        flag = False

       
    
    if(flag == True):#seq number go next if receive good package
        count += 1

print('name: BrianSun') #print name, date and time, 200bytes checksum
print('date and time: ', datetime.datetime.now())
print('checksum: ', checksum200)
print('sent total: ', sent_total)
print('receive total: ', received_total)
print('corrupted message: ', corrupted_message)

# clientSocket.close()


