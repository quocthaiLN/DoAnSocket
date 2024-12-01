import socket
import getpass # to hide password: ****
import time
#HOST, PORT
HOST = socket.gethostname()
PORT = 12000


# test
def uploadFile(client):
    msg = input("Sever: Nhap vao ten file hoac duong dan file: ")
    client.sendall(msg.encode('utf-8'))
    resp = client.recv(1024)
    resp = resp.decode('utf-8')
    if resp == "Failed":
        print("Sever: Tai file len that bai")
    if resp == "Success":
        print("Sever: Tai file len thanh cong")

def downloadFile(client):
    msg = input("Sever: Nhap vao ten file hoac duong dan file: ")
    client.sendall(msg.encode('utf-8'))
    resp = client.recv(1024)
    resp = resp.decode('utf-8')
    if resp == "Failed":
        print("Sever: Tai file ve that bai")
    if resp == "Success":
        print("Sever: Tai file ve thanh cong")

def menu():
    print("0. Exit")
    print("1. Download File")
    print("2. Upload File")

def login(client):

    # Nhận yêu cầu từ server để nhập thông tin
    request = client.recv(1024).decode('utf-8')
    print(request)
            

    username = input("\nUsername: ")
    password = input("Password: ")

    login_information = f"{username},{password}"
    client.sendall(login_information.encode('utf-8'))

    # Nhận phản hồi từ server
    resp = client.recv(1024).decode('utf-8')
    if resp == "Successful":
        print("Login Successful")
        return True
    else:
        print("Login unsuccessfully")
        return False


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    client.connect((HOST, PORT))
    print("Ket noi thanh cong voi Sever.")

    while not login(client): 
        continue
    connect = True
    while connect:
        menu()
        choice = int(input("Nhap lua chon cua ban: "))
        if choice == 0:
            msg = "exit"
            again_check = input("Ban co chac rang muon ngat ket noi chu?(Y/N): ")
            if again_check == "Y":
                client.sendall(msg.encode('utf-8'))
                print("Ban da ngat ket noi khoi Server.")
                connect = False
            else:
                continue
        if choice == 1:
            msg = "downloadFile"
            client.sendall(msg.encode('utf-8'))
            downloadFile(client)
        if choice == 2:
            msg = "uploadFile"
            client.sendall(msg.encode('utf-8'))
            uploadFile(client)
except socket.timeout:
    print("Server dang day.")
except:
    print("Khong the ket noi voi Server.")

client.close()
