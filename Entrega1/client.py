import socket
import os
import zlib
from time import sleep

def checksum_calculator(data):
    checksum = zlib.crc32(data)
    return checksum

serverIP = "10.0.0.189"
serverPort = 5001

print("1 - Enviar arquivos para teste")
print(" Obs.: Você precisa ter um arquivo 'teste.txt' na sua máquina")
print("2 - Chat Cliente-Servidor")

option = int(input())

if option == 1:

    gap = "<gap>"
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
        if clientMessage == "SAIR":
            flag = 0

        udpSocketClient.sendto(bytes(clientMessage,"utf8"), destination) # Com a função "bytes", converto a mensagem do cliente de string para bytes para ser enviada pelo "sendTo"

        # Recebimento das mensagens do servidor
        serverMessage, source = udpSocketClient.recvfrom(1024)
        serverMessage = serverMessage.decode('ASCII')

        print(source[0], ":", serverMessage)

    udpSocketClient.close()