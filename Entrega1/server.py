import socket
import os
import zlib

def checksum_calculator(data):
    checksum = zlib.crc32(data)
    return checksum


serverIP = ''
serverPort = 5001





print("1 - Receber arquivos para teste")
print("2 - Chat Cliente-Servidor")

option = int(input())

if option == 1:

    gap = "<gap>"

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
        clientMessage = clientMessage.decode('ASCII') # Faço a conversão de bytes para string de volta
        if clientMessage == "SAIR":
            print ("A conexão foi encerrada pelo cliente...")
            flag = 0
        else:
            print (source[0], ":", clientMessage)
            response = "Entendido!"
            udpSocketServer.sendto(bytes(response, "utf8"), source)
            
    udpSocketServer.close()
