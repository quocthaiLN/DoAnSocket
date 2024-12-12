import socket
import os
import time
import getpass # to hide password: ****
import time


# Duong dan toi thu muc chua cac file duoc tai xuong o client
Path_Client = "DataClient"
#HOST, PORT
HOST = socket.gethostname()
PORT = 12000


# Lay tu ki tu "/" cuoi cung tro ve sau trong duong dan hoac ten file
def name(file_name):
    res = ""
    # Dem so ki tu "/" de tim den ki tu "/" cuoi cung
    cnt = 0
    for chara in file_name:
        if chara == "/":
            cnt += 1
    i = 0
    # Lay ten cua file bat dau tu ki tu "/" cuoi hoac lay nguyen ten file
    for charac in file_name:
        if charac == "/" and i < cnt:
            i += 1
        if i == cnt:
            res += charac
    return res

# Kiem tra xem co ki tu "/" trong ham o tren chua
def check(s):
    if s[0] == "/":
        return True
    return False

# Lay phan ten file va khong lay them phan mo rong
def getNameWithNotExten(name):
    res = name[0 : name.index(".")]
    return res

# Lay phan mo rong cua file
def getExten(name):
    res = name[name.index(".") : len(name)]
    return res

# Ham xoa man hinh
def cleanScreen():
    os.system("cls")

# Kiem tra xem file co ton tai khong
def checkExist(path):
    if os.path.isfile(path):
        return True
    return False

# Kiem tra xem folder co ton tai khong
def checkFolderExist(path):
    if os.path.isdir(path):
        return True
    return False

# Ham upload file
def uploadFile(client, msg):
    # Lay kich thuoc cua file roi gui toi cho sever va nhan thong bao cua sever neu gui thanh cong
    size_send = os.path.getsize(msg)
    client.sendall(str(size_send).encode("utf-8"))
    size_resp = client.recv(1024).decode("utf-8")
    # Mo va lam viec voi file
    with open(msg, "rb") as ifs:
        while 1:
            # Doc du lieu tu file va thoat ra khoi vong lap neu khong doc duoc du lieu nua
            data = ifs.read(1024)
            if not data:
                break
            # Co gang du lieu va nhan thong bao tu sever  
            try:
                client.sendall(data)
            except Exception as e:
                print(f"There was an error when uploading file {msg} / Connect Error with sever.")
                return False
            try:
                resp = client.recv(1024).decode("utf-8")
            except Exception as e:
                print(f"There was an error when uploading file {msg} / Connect Error with sever.")
                return False
    # Gui thong bao "xong" toi cho sever de sever gui lai trang thai 
    client.sendall("xong".encode("utf-8"))
    resp_sta = client.recv(1024).decode("utf-8")
    # Gui thong bao da nhan trang thai va nhan thong bao "success" hay "failed" tu sever gui toi
    client.sendall("da nhan".encode("utf-8"))
    resp = client.recv(1024).decode("utf-8")
    if resp == "Success":
        print(f"Sever: The file {msg} has been successfully uploaded to the server. {resp_sta}") 
    else:
        print(f"Sever: The file {msg} has been unsuccessfully uploaded to the server. {resp_sta}")

# Ham download file
def downloadFile(client, msg):
    # Nhan trang thai xem file co ton tai tren sever hay co bi cam tai khong
    check_status = client.recv(1024).decode("utf-8")
    if check_status == "forbidden file":
        print("Sever: File is in list forbidden file. Can't download this file")
        return
    if check_status == "Not exist":
        print("Sever: File is not exist!!!")
        return
    else:
        resp = "Received"
        client.sendall(resp.encode("utf-8"))

    #tao duong dan den noi luu tru file
    tmp = name(msg)
    if not check(tmp):
        tmp = "/" + tmp
    name_with_not_exten = getNameWithNotExten(tmp)
    exten = getExten(tmp)
    file_write = Path_Client + tmp
    #kiem tra xem trong thu muc sever co file tren chua neu co thi them so 1,2,3,.. o sau de khac voi file cu
    i = 1
    while os.path.isfile(Path_Client + tmp):
            tmp = name_with_not_exten + "(" + str(i) + ")" + exten
            file_write = Path_Client + tmp
            i += 1

    # Nhan kich thuoc file va gui lai thong bao toi sever
    size_recv = client.recv(1024).decode("utf-8")
    size = int(size_recv)
    size_resp = "Received"
    client.sendall(size_resp.encode("utf-8"))

    # Tuong tu nhu upload file o sever
    ofs = open(file_write, "wb")
    sw = 0
    while size > sw:
        try:
            data = client.recv(1024)
        except Exception as e:
            print(f"Client: There was an error when download file {msg}/ Connect Error with sever.")
            return False
        if not data:
            break
        ofs.write(data)
        sw += len(data)
        try:
            client.sendall(str(sw).encode("utf-8"))
        except:
            print(f"Client: There was an error when download file {msg}/ Connect Error with sever.")
            return False
    ofs.close()

    # Nhan thong bao tu sever
    resp = client.recv(1024).decode("utf-8")
    if resp == "Success":
        print(f"Sever: The file has been successfully downloaded and is currently stored at {file_write}. ")
    else:
        print(f"Sever: File download failed. Connection error!")

def uploadFilesInFolderSequentially(client, msg):
    # Lay danh sach cac ten file trong folder
    fileName = os.listdir(msg)
    # Gui so luong file cho sever
    client.sendall(str(len(fileName)).encode("utf-8"))
    size_resp = client.recv(1024).decode("utf-8")
    # Nhan trang thai khong thanh cong neu so luong file la 0
    if size_resp != "Received":
        print(f"Sever: {size_resp}")
        return
    # Gui ten file va upload file
    for file in fileName:
        client.sendall(file.encode("utf-8"))
        fileRep = client.recv(1024).decode("utf-8")
        uploadFile(client, msg + "/" + file)
    # Gui thong bao da gui xong
    client.sendall("Success".encode("utf-8"))
    # Nhan trang thai tu sever gui ve
    res = client.recv(1024).decode("utf-8")
    print(res)

def menu():
    print("0. Exit")
    print("1. Upload File")
    print("2. Download File")
    print("3. Upload Files In Folder Sequentially")
    
def client_send(client, data):
    try:
        client.sendall(data.encode("utf-8"))
    except socket.error: #BẮT LỖI TIME-OUT, SERVER TỰ NGẮT KẾT NỐI BẰNG CLOSE()
        print(f"Server: Disconnected with sever.")
        client.close()
    except ConnectionResetError:
        print(f"Server: Connection was abruptly terminated with sever.")
        client.close()
    except Exception as e:
        print(f"An error {e} occurred while sending data to the server.")
        client.close()


def client_receive(client):
    try:
        data = client.recv(1024).decode("utf-8")
        if not data:
            print("Server đã đóng kết nối.")
            client.close()
        else:
            return data
    except socket.error: #BẮT LỖI TIME-OUT, SERVER TỰ NGẮT KẾT NỐI BẰNG CLOSE()
        print(f"Server: Disconnected with sever.")
        client.close()
    except ConnectionResetError:
        print(f"Server: Connection was abruptly terminated with sever.")
        client.close()
    except Exception as e:
        print(f"An error {e} occurred while sending data to the server.")
        client.close()
    return None
    
# Lay ten file tai khong thanh cong
def getErrorDownload(before_error_download):
    start_of_path_idx = before_error_download.find(" ") + 1
    path = before_error_download[start_of_path_idx:]
    start_of_filename_idx = path.find("/") + 1
    error_file= path[start_of_filename_idx:]
    return error_file

def login(client):
    status = client_receive(client)
    os.system("cls")
    # In ra man hinh da ket noi thanh cong voi sever
    print(status)
    res = client_send(client, "success")
    # Nhan yeu cau nhap ten dang nhap va mat khau
    reply = client_receive(client)
    print(reply)
    username = input("\nUsername: ")
    password = input("Password: ")

    # Gui thong tin ten dang nhap va mat khau toi sever
    login_information = f"{username},{password}"
    client_send(client, login_information)

    # Nhận phản hồi từ server
    resp = client_receive(client)
    if resp == "Successful":
        print("Login Successful")
        return True
    else:
        print("Login unsuccessfully")
        return False


# --------------------------- main ----------------


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print(f"Connecting to the server, please wait.")
        # Neu dang nhap khong thanh cong phai tiep tuc dang nhap cho toi khi thanh cong hoac thoat
        while not login(client): 
            continue
        connect = True
        while connect:
            menu()
            choice = input("Sever: Enter your choice: ")
            # Kiem tra xem client nhap co hop le khong
            if choice > '9' or choice < '0':
                print("Sever: Your input is invalid. Please try again!!!")
                continue
            else:
                choice = int(choice)
            match choice:
                # Ngat ket noi voi sever
                case 0:
                    msg = "exit"
                    again_check = input("Sever: Are you sure you want to disconnect?(Y/N): ")
                    if again_check == "Y":
                        client.sendall(msg.encode("utf-8"))
                        print("Sever: You have disconnected from the server!")
                        connect = False
                    else:
                        break
                case 1:
                    # Dat co de neu client nhap CANCEL thi se khong thuc hien upload
                    flag = True
                    msg = "uploadFile"
                    # Gui thong bao se uploa file den sever
                    client.sendall(msg.encode("utf-8"))

                    # Nhan yeu cau nhap duong dan tu sever
                    resp = client.recv(1024).decode("utf-8")
                    # Nhap yeu cau gui toi sever
                    while 1:
                        print("Type 'CANCEL' to return to the menu!!!")
                        msg = input(f"(Sever request) - {resp}")
                        if msg == "CANCEL":
                            client.sendall(msg.encode("utf-8"))
                            rec = client_receive(client)
                            flag = False
                            break
                        if not checkExist(msg):
                            print("The file does not exist. Please enter again!!!")
                            continue
                        client.sendall(msg.encode("utf-8"))
                        rec = client_receive(client)
                        break

                    # Neu nhap duong dan dung thi thuc hien upload
                    if flag == True:
                        uploadFile(client, msg)

                case 2:
                    # Gui yeu cau download toi cho sever
                    msg = "downloadFile"
                    client.sendall(msg.encode("utf-8"))
                    # Kiem tra xem client truoc day co tung co file tai loi khong
                    before_error_download = client.recv(1024).decode("utf-8")
                    if before_error_download != "NoError":
                        # Lay ten file tai loi
                        error_file = getErrorDownload(before_error_download)
                        print(f"You previously attempted to download the file {error_file}, but it was interrupted during your last session. Would you like to resume the download? (Y/N)")
                        continue_download  = input()
                        # Gui yeu cau tiep tuc va tiep tuc tai
                        if continue_download == "Y":
                            client.sendall(continue_download.encode("utf-8"))
                            time.sleep(0.1)
                            client.sendall(error_file.encode("utf-8"))
                            downloadFile(client, error_file)
                        # Gui yeu cau khong tiep tuc va tiep tuc tai file khac
                        else:
                            client.sendall(continue_download.encode("utf-8"))
                            time.sleep(0.1)
                            flag = True
                            while 1:
                                print("Type 'CANCEL' to return to the menu!!!")
                                msg = input(f"Sever: Enter the name of the file you want to download: ")
                                if msg == "CANCEL":
                                    client.sendall(msg.encode("utf-8"))
                                    flag = False
                                    break
                                client.sendall(msg.encode("utf-8"))
                                break
                            if flag == True:
                                downloadFile(client, msg)
                    # Neu khong co file tai loi truoc do thi tai file
                    else:
                        flag = True
                        while 1:
                            print("Type 'CANCEL' to return to the menu!!!")
                            msg = input(f"Sever: Enter the name of the file you want to download: ")
                            if msg == "CANCEL":
                                client.sendall(msg.encode("utf-8"))
                                flag = False
                                break
                            client.sendall(msg.encode("utf-8"))
                            break
                        if flag == True:
                            downloadFile(client, msg)

                case 3:
                    # Gui thong bao den cho sever
                    msg = "uploadFilesInFolderSequentially"
                    client.sendall(msg.encode("utf-8"))
                    flag = True
                    #Nhan yeu cau nhap duong dan folder tu sever
                    resp = client.recv(1024).decode("utf-8")
                    while 1:
                        print("Type 'CANCEL' to return to the menu!!!")
                        msg = input(f"(Sever request) - {resp}")
                        if msg == "CANCEL":
                            client.sendall(msg.encode("utf-8"))
                            rec = client_receive(client)
                            flag = False
                            break
                        if not checkFolderExist(msg):
                            print("The folder does not exist. Please enter again!")
                            continue
                        client.sendall(msg.encode("utf-8"))
                        rec = client_receive(client)
                        break
                    if flag == True:
                        uploadFilesInFolderSequentially(client, msg)

                case default:
                    print("Your input is invalid. Please try again.")

    except Exception as e:
        print(F"Cannot connect to the server, Error: {e}")
    input()
    client.close()

if __name__ == "__main__":
    main()
#C:/Users/Admin/Documents/vs code/vs code python/anh.bin
