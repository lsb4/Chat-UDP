import socket
import os
from time import sleep

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

serverIP = "127.0.0.1"
serverPort = 5001

seqNumber = 0

print("1 - Enviar arquivos para teste")
print(" Obs.: Você precisa ter um arquivo 'teste.txt' na sua máquina")
print("2 - Chat Cliente-Servidor")

option = int(input())

gap = "<gap>"

if option == 1:

    fileName = "teste.txt"
    fileSize = os.path.getsize(fileName)


    udpSocketClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket do cliente para enviar arquivos para o servidor

    destination = (serverIP, serverPort)

    udpSocketClient.connect(destination)
    udpSocketClient.send(f"{fileName}{gap}{fileSize}".encode('utf-8'))


    with open(fileName, "rb") as file_:
        while True:
            bytesRead = file_.read(4096) # Lê os bytes do arquivo

            if not bytesRead: # Se não tem mais bytes, acabou o arquivo, então para de enviar
                print("File sended!")
                udpSocketClient.sendall('file_download_exit'.encode('utf-8'))
                break
            udpSocketClient.sendall(bytesRead) # Sendall é uma variação do socket.send(), só que fica enviando até terminar tudo
            sleep(0.001)

    udpSocketClient.close()
    file_.close()

elif option == 2:

    flag = 1

    udpSocketClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket do cliente para enviar mensagens para o servidor

    destination = (serverIP, serverPort) # "Socket" do servidor que o cliente vai enviar mensagem

    while flag == 1:

        # Envio das mensagens do cliente
        clientMessage = input()
        checksum = checksum_calc(clientMessage)
    
        if clientMessage == "SAIR":
            flag = 0
        
        udpSocketClient.sendto(f"{checksum}{gap}{clientMessage}{gap}{seqNumber}".encode('utf-8'), destination)

        isACK, source = udpSocketClient.recvfrom(4096) # Recebemos os dados contendo nome e tamanho do arquivo
        isACK = isACK.decode('utf-8')

        ackChecksum, ackMessage, ackSeqNumber = isACK.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

        if ackChecksum != str(checksum_calc(ackMessage)) or ackSeqNumber != seqNumber:
            udpSocketClient.sendto(f"{checksum}{gap}{clientMessage}{gap}{seqNumber}".encode('utf-8'), source)

            isACK2, source = udpSocketClient.recvfrom(4096) # Recebemos os dados contendo nome e tamanho do arquivo
            isACK2 = isACK2.decode('utf-8')

            ack2Checksum, ack2Message, ack2SeqNumber = isACK2.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split

            if ack2Checksum != str(checksum_calc(ack2Message)) or ack2SeqNumber != seqNumber:
                print("SeqNumber:", seqNumber)
                flag = 0

        # Recebimento das mensagens do servidor
        seqNumber = 1 - seqNumber
        pktMessage, source = udpSocketClient.recvfrom(1024)
        pktMessage = pktMessage.decode('utf-8')

        pktChecksum, pktMessage, pktSeqNumber = pktMessage.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split
        mainMessage = pktMessage

        if str(checksum_calc(pktMessage)) != pktChecksum:
            message = bytes('ACK', 'utf8')
            check = checksum_calc(message)
            print("Corrupted 1")
            udpSocketClient.sendto(f"{check}{gap}{message}{gap}{1 - seqNumber}".encode('utf-8'), source)

            retry, aux = udpSocketClient.recvfrom(1024) # O 1024 representa o tamanho do buffer
            retry = retry.decode('utf-8')

            retryChecksum, retryMessage, retrySeqNumber = retry.split(gap) # Separamos o nome e o tamanho usando a variável 'gap' no split
            mainMessage = retryMessage

            if str(checksum_calc(retryMessage)) != retryChecksum:
                print("Corrupted 2... bye!")
                udpSocketClient.sendto(f"{check}{gap}{message}{gap}{1 - seqNumber}".encode('utf-8'), source)
                flag = 0
        
        print(source[0], ":", mainMessage)


    udpSocketClient.close()