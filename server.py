import socket
import threading
import time

#Khai bao HOST, PORT
HOST = socket.gethostname()
PORT = 12000

#Ham ket noi voi client
def recvData(client, addr) :
    print(f"Connection from {addr} has been established!") #Thong bao da ket noi voi client
    try:
        data = ""#Du lieu nhan duoc tu client
        while True:
            client.settimeout(600)#Dat thoi gian timeout la 10 phut
            try:
                
                data = client.recv(1024)#Nhan data tu client
                

                data = data.decode('utf-8')#Decode data nhan duoc
              
                if(data == "exit"):#Neu client yeu cau exit
                    print(f"Client {addr}: wants to disconect.")#Thong bao voi Server la Client muon exit
                    client.send(bytes("Are you sure you want to disconnect?(Y/N)", "utf-8"))#Server gui thong bao cho Client, m chac chua
                    data = client.recv(1024)#Nhan phan hoi tu Client
                    data = data.decode('utf-8')
                    if(data == "Y"):#Neu phan hoi la Y thi ngat ket noi, nguoc laij thi tiep tuc gia tiep
                        client.close()
                        print(f"Client {addr}: has been disconnected.")
                        break
                    else:
                        print(f"Client {addr}: does not want to disconect.")
                    
                else:
                    print(f"Client {addr}: {data}")#Neu khong exit thi in data ma Client gui ra
            except socket.timeout:#Neu het thoi gian timeout ma khong co giao tiep nao duoc thuc hien thi bao loi va ngat ket noi
                 client.close()
                 print(f"Client {addr}: is not responding for too long.")
                 break
                
    except:
        print("Connect Error")





sever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sever.bind((HOST, PORT))
NumsOfClient = int(input("The number of client: "))
sever.listen(NumsOfClient)
print("Waiting for connection.....")
count = 0
while count < NumsOfClient:
    client, addr = sever.accept()
    thread = threading.Thread(target = recvData, args = (client, addr))
    thread.daemon = False
    thread.start()
    count += 1
sever.close()    
