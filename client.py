import socket

HOST = socket.gethostname();
PORT = 12000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, 12000))
    print("Connection to Server has been established!")
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
