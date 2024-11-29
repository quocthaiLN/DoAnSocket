import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((socket.gethostname(), 2810))
    print("Ket noi thanh cong voi sever!!!")
    msg = ""
    while msg != "exit":
        msg = input("Client: ")
        client.sendall(msg.encode('utf-8'))
    respFromSever = ""
    tmpAddr = client.getsockname()
    while respFromSever != "stop" :
        respFromSever = client.recv(1024)
        respFromSever = respFromSever.decode('utf-8')
        if respFromSever == "stop":
            break
        print(f"Sever: {respFromSever}")
except:
    print("Connect error")
client.close()
