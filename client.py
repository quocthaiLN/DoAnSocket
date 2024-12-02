import socket
import os
import time
import getpass # to hide password: ****
import time

PathClient = "DataClient"

#lay tu ki tu '/' cuoi cung tro ve sau trong duong dan hoac ten file
def name(fileName):
    res = ""
    cnt = 0
    for chara in fileName:
        if chara == '/':
            cnt += 1
    i = 0
    for charac in fileName:
        if charac == '/' and i < cnt:
            i += 1
        if i == cnt:
            res += charac
    return res

#kiem tra xem co ki tu '/' trong ham o tren chua
def check(s):
    if s[0] == '/':
        return True
    return False

#lay phan ten file va khong lay them phan mo rong
def getNameWithNotExten(name):
    res = name[0 : name.index(".")]
    return res

#lay phan mo rong cua file
def getExten(name):
    res = name[name.index(".") : len(name)]
    return res

def cleanScreen():
    os.system("cls")

def checkExist(path):
    if os.path.isfile(path):
        return True
    return False



#HOST, PORT
HOST = socket.gethostname()
PORT = 12000

def uploadFile(client):
    #Nhan yeu cau nhap duong dan tu sever
    resp = client.recv(1024).decode('utf-8')
    while 1:
        print("Nhap CANCEL de thoat!!!")
        msg = input(f"(Sever request) - {resp}")
        if msg == 'CANCEL':
            client.sendall(msg.encode('utf-8'))
            return
        if not checkExist(msg):
            print("File khong ton tai. Yeu cau nhap lai!!!")
            continue
        client.sendall(msg.encode('utf-8'))
        break
    size = os.path.getsize(msg)
    client.sendall(str(size).encode('utf-8'))
    sizeResp = client.recv(1024).decode('utf-8')
    
    ifs = open(msg, "rb")
    while 1:
        data = ifs.read(1024)
        if not data:
            break
        client.sendall(data)
    ifs.close()
    respSta = client.recv(1024).decode('utf-8')
    client.sendall("da nhan".encode('utf-8'))
    resp = client.recv(1024).decode('utf-8')
    if resp == "Success":
        print(f"Sever: Da upload file len sever thanh cong. {respSta}")
    else:
        print(f"Sever: Upload file len sever that bai. {respSta}")

def downloadFile(client):
    #Nhan yeu cau nhap duong dan tu sever
    resp = client.recv(1024).decode('utf-8')
    print("Nhap CANCEL de thoat!!!")
    #nhap vao ten file
    msg = input(f"(Sever request) - {resp}")
    if msg == 'CANCEL':
        client.sendall(msg.encode('utf-8'))
        return
    #gui ten file hoac duong dan
    client.sendall(msg.encode('utf-8'))
    #gui trang thai xem file co ton tai tren sever hay khong
    checkStatus = client.recv(1024).decode('utf-8')
    if checkStatus == 'Not exist':
        print("File khong ton tai!!!")
        return
    else:
        resp = "Da nhan duoc"
        client.sendall(resp.encode('utf-8'))
    #tao duong dan den noi luu tru file
    tmp = name(msg)
    if not check(tmp):
        tmp = '/' + tmp
    nameWithNotExten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    fileWrite = PathClient + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(PathClient + tmp):
            tmp = nameWithNotExten + "(" + str(i) + ")" + exten
            fileWrite = PathClient + tmp
            i += 1
    sizeRecv = client.recv(1024).decode('utf-8')
    size = int(sizeRecv)
    sizeResp = "Nhan thanh cong"
    client.sendall(sizeResp.encode('utf-8'))
    ofs = open(fileWrite, "wb")
    sw = 0
    while size > sw:
        data = client.recv(1024)
        if not data:
            break
        ofs.write(data)
        sw += len(data)
    ofs.close()
    client.sendall(str(sw).encode('utf-8'))
    # respSta = client.recv(1024).decode('utf-8')
    # client.sendall("da nhan".encode('utf-8'))
    resp = client.recv(1024).decode('utf-8')
    if resp == "Success":
        print(f"Sever: Da download file thanh cong. File dang duoc luu tru tai {fileWrite} ")
    else:
        print(f"Sever: Download file that bai. Loi ket noi!")


def menu():
    print("0. Exit")
    print("1. Upload File")
    print("2. Download File")
    

def login(client):

    # Nhận yêu cầu từ server để nhập thông tin
    # client.settimeout(5)    
    # try:
    request = client.recv(1024).decode('utf-8')

    if request == "Server da day.":
        print(request)
        client.close()
        return
    else:
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

# --------------------------- main ----------------
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
            msg = "uploadFile"
            client.sendall(msg.encode('utf-8'))
            uploadFile(client)

        if choice == 2:
            msg = "downloadFile"
            client.sendall(msg.encode('utf-8'))
            downloadFile(client)
except socket.timeout:
    print("Server dang day.")

except:
    print("Khong the ket noi voi Server.")

client.close()
#C:/Users/Admin/Documents/vs code/vs code python/anh.bin