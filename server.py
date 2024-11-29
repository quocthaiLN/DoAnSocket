import socket
import threading


def recvData(client, addr) :
    print(f"Client {addr} ket noi thanh cong!!!")
    try:
        data = ""
        while data != "exit":
            data = client.recv(1024);
            data = data.decode('utf-8')
            if data == "exit":
                break
            print(f"Client {addr}: {data}")
        resp = ""
        while resp != "stop" :
            resp = input("Sever: ")
            client.sendall(resp.encode('utf-8'))
    except:
        print("Connect Error")
    client.close()

sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sever.bind((socket.gethostname(), 2810))
NumsOfClient = int(input("Nhap vao so luong client:"))
sever.listen(NumsOfClient)
print("Sever dang lang nghe.....")
count = 0
while count < NumsOfClient:
    client, addr = sever.accept()
    thread = threading.Thread(target = recvData, args = (client, addr))
    thread.daemon = False
    thread.start()
    count += 1
sever.close()    
