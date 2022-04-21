import socket
import os
import zlib

def carry(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum_calc(msg):
    s = 0
    if len(msg) % 2 == 0:
        pass
    else:
        msg = msg + 's'
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry(s, w)
    return ~s & 0xffff

def make_pkt(message, seqNum):
    checksum = checksum_calc(message)
    return str({
        'cksum': checksum,
        'data': message,
        'seq': seqNum
    }).encode()

serverIP = ''
serverPort = 5001

seqNumber = 0

print("1 - Receber arquivos para teste")
print("2 - Chat Cliente-Servidor")

option = int(input())

gap = "<gap>"

if option == 1:

    udpSocketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server = (serverIP, serverPort)

    print("Aguardando conexão...")
    udpSocketServer.bind(server) # O bind serve para que o servidor comece a escutar o IP e a Porta definida anteriormente

    fileInfo, source = udpSocketServer.recvfrom(4096) # Recebemos os dados contendo nome e tamanho do arquivo
    fileInfo = fileInfo.decode('utf-8')
    print("File information received!")

    fileName, fileSize = fileInfo.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

    fileName = os.path.basename(fileName) # O caminho que recebemos é o do cliente, então temos que tirar esse caminho, pois vai ser diferente do servidor

    with open(fileName, "wb") as file_:
        print("Reading file...")    
        while True:
            bytesRead = udpSocketServer.recv(4096)

            if bytesRead == b'file_download_exit': # Se nada for recebido, acabou o arquivo, então para de receber
                print("File Downloaded")
                break
            
            file_.write(bytesRead) # Escreve o que foi recebido no arquivo
            
    file_.close()
    udpSocketServer.close()


elif option == 2:

    flag = 1

    udpSocketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server = (serverIP, serverPort)

    udpSocketServer.bind(server) # O bind serve para que o servidor comece a escutar o IP e a Porta definida anteriormente

    while flag == 1:
        clientMessage, source = udpSocketServer.recvfrom(1024) # O 1024 representa o tamanho do buffer
        clientMessage = clientMessage.decode('utf-8')

        pktChecksum, pktMessage, pktSeqNumber = clientMessage.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

        if str(checksum_calc(pktMessage)) != pktChecksum:
            message = bytes('ACK', 'utf8')
            check = checksum_calc(message)
            print("Corrupted 1")
            udpSocketServer.sendto(f"{check}{gap}{message}{gap}{1 - seqNumber}".encode('utf-8'), source)

            retry, aux = udpSocketServer.recvfrom(1024) # O 1024 representa o tamanho do buffer
            retry = retry.decode('utf-8')

            retryChecksum, retryMessage, retrySeqNumber = retry.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

            if str(checksum_calc(retryMessage)) != retryChecksum:
                print("Corrupted 2... bye!")
                udpSocketServer.sendto(f"{check}{gap}{message}{gap}{1 - seqNumber}".encode('utf-8'), source)
                flag = 0            

        if pktMessage == "SAIR":
            print ("A conexão foi encerrada pelo cliente...")
            flag = 0
        else:
            message = "ACK"
            check = checksum_calc(message)
            udpSocketServer.sendto(f"{check}{gap}{message}{gap}{seqNumber}".encode('utf-8'), source)
            print (source[0], ":", pktMessage)
            seqNumber = 1 - seqNumber

            response = "Entendido!"
            respCheck = checksum_calc(response)
            udpSocketServer.sendto(f"{respCheck}{gap}{response}{gap}{seqNumber}".encode('utf-8'), source)

            isACK, source = udpSocketServer.recvfrom(4096) # Recebemos os dados contendo nome e tamanho do arquivo
            isACK = isACK.decode('utf-8')

            ackChecksum, ackMessage, ackSeqNumber = isACK.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

            if ackChecksum != str(checksum_calc(ackMessage)) or ackSeqNumber != seqNumber:
                udpSocketServer.sendto(f"{respCheck}{gap}{response}{gap}{seqNumber}".encode('utf-8'), source)

                isACK2, source = udpSocketServer.recvfrom(4096) # Recebemos os dados contendo nome e tamanho do arquivo
                isACK2 = isACK2.decode('utf-8')

                ack2Checksum, ack2Message, ack2SeqNumber = isACK2.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

                if ack2Checksum != str(checksum_calc(ack2Message)) or ack2SeqNumber != seqNumber:
                    flag = 0

            
            
    udpSocketServer.close()