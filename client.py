import socket
import getpass # to hide password: ****
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

    username = input("Username: ")
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
    client.connect((socket.gethostname(), 2810))
    print("Ket noi thanh cong voi sever!!!")

    while not login(client): 
        continue

    while 1:
        menu()
        choice = int(input("nhap vao lua chon cua ban: "))
        if choice == 0:
            msg = "exit"
            client.sendall(msg.encode('utf-8'))
            break
        if choice == 1:
            msg = "downloadFile"
            client.sendall(msg.encode('utf-8'))
            downloadFile(client)
        if choice == 2:
            msg = "uploadFile"
            client.sendall(msg.encode('utf-8'))
            uploadFile(client)
except:
    print("Connect error")
client.close()
