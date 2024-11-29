import socket

#Khai bao HOST, PORT
HOST = socket.gethostname();
PORT = 12000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))#Ket noi vs Server
    print("Connection to Server has been established!")
    msg = ""
    while True:
        msg = input("Client: ")#Data ma Client muon gui
        client.sendall(msg.encode('utf-8'))

        if msg == "exit":#Neu Client muon exit
            data = ""
            data = client.recv(1024)
            data = data.decode("utf-8")
            print(f"Server: {data}")
            msg = input("Your decision(Y/N): ")
            client.sendall(msg.encode('utf-8'))
            if msg == "Y":
                print("You just disconnected from the Server.")
                break
            else:
                continue   
except:
    print("Connect error")
client.close()
