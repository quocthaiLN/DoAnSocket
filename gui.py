from tkinter import *
import socket
import os
import time

FONT = "JetBrains Mono"
BTN_COLOR = "#A1EEBD"
WIDTH_BTN = 18 # width of featured buttons
PathClient = "DataClient"
PathSever = "DataSever"  
PathUsers = "users.csv"

# Các hàm để xử lý đường dẫn
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

class DownloadPage(Frame):
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)
        # Main label
        mainLabel = Label(self, text="Download Page", font=(FONT, 22, "bold"))
        mainLabel.place(x = 125, y = 50)
        # Notr label
        lb_note = Label(self, text = "Path", font = (FONT, 12, "bold"))
        lb_note.place(x = 40, y = 120)
        # Entry path file
        self.entry_path = Entry(self, width = 40, font = (FONT, 10), fg = "blue")
        self.entry_path.focus()
        self.entry_path.place(x = 125 - 30, y = 120, height = 24)

        # Button 
        btn_select_file = Button(self, text = "Select file", font = (FONT, 16, "bold"), bg = "PaleGreen", command = lambda: app_pointer.downloadFile(self, client))
        btn_select_file.place(x = 150, y = 200)



class UploadPage(Frame):
    def __init__(self, parent, main_menu_pointer):
        Frame.__init__(self, parent)

        mainLabel = Label(self, text="Upload Page", font=(FONT, 22, "bold"))
        mainLabel.pack()


class MainMenu(Frame):
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)
        # ----------------- Widget --------------------------
        lb_main = Label(self, text = "Main Menu", font = (FONT, 20, "bold"))
        lb_main.place(x = 150, y = 30)

        # Button
        btn_download_file = Button(self, text = "Download file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN, command = lambda: app_pointer.show_page(DownloadPage))
        btn_download_file.place(x = 130, y = 120)

        btn_download_folder = Button(self, text = "Download folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_download_folder.place(x = 130, y = 160)

        btn_upload_file = Button(self, text = "Upload file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_upload_file.place(x = 130, y = 200)

        btn_upload_folder = Button(self, text = "Upload folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_upload_folder.place(x = 130, y = 240)

        btn_exit = Button(self, text = "Exit", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_exit.place(x = 130, y = 280)

        
        
    # def show_download_page(self, pageName):
    #     self.frames[pageName].tkraise()
        
    # def downloadFile(self, curFrame: Frame, sck: socket):
    #     msg = input("Sever: Nhap vao ten file hoac duong dan file: ")
    #     sck.sendall(msg.encode('utf-8'))
    #     resp = sck.recv(1024)
    #     resp = resp.decode('utf-8')
    #     if resp == "Failed":
    #         print("Sever: Tai file ve that bai")
    #     if resp == "Success":
    #         print("Sever: Tai file ve thanh cong")
    #     pass

class LoginPage(Frame):
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)
        # Label - header
        lb_head = Label(self, text = "Login", font = (FONT, 15))
        lb_head.place(x = 200, y = 140) # 10
        # Label username
        lb_username = Label(self, text = "username", font = (FONT, 11))
        lb_username.place(x = 70, y = 190)

        # Label password
        lb_password = Label(self, text = "password", font = (FONT, 11))
        lb_password.place(x = 70, y = 240)

        # Label notice
        self.lb_notice = Label(self, text = "", font = (FONT, 8), fg = "red")
        self.lb_notice.place(x = 165, y = 267)
        # Entry username
        self.entry_username = Entry(self, width = 25, font = (FONT, 12), bd = 0.25)
        self.entry_username.place(x = 165, y = 192)
        self.entry_username.focus()

        # Entry password
        self.entry_password = Entry(self, width = 25, font = (FONT, 12), bd = 0.25)
        self.entry_password.place(x = 165, y = 242)

        # Button
        btn_login = Button(self, text = "Sign in", font = (FONT, 9, "bold"), bg = "#80C4E9", command = lambda: app_pointer.login(self, client))
        btn_login.place(x = 195, y = 290)



class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.title("Application")
        self.geometry("450x550")
        self.resizable(width = False, height = False)
        self.attributes("-topmost", True)
        # self["bg"] = "white"
        # login_frame = LoginPage(container)
        # home_frame = HomePage(container)

        # Đoạn code dùng nếu muốn thay đổi các frame
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Tạo một dictionary để lưu các class page
        # Dùng vòng for để grid các frame này, thay vì làm tuần tự
        self.frames = {}
        for F in (LoginPage, MainMenu, DownloadPage, UploadPage):
            frame = F(container, self)
            frame.grid(row = 0, column = 0, sticky = "nsew")
            self.frames[F] = frame
        
        self.frames[LoginPage].tkraise()

    def show_page(self, class_name):
        self.frames[class_name].tkraise()

    def login(self, curFrame, sck):
        # Nhận yêu cầu từ server để nhập thông tin
        request = sck.recv(1024).decode('utf-8')
        print(request)
        try:
            username = curFrame.entry_username.get()
            password = curFrame.entry_password.get()

            if username == "" or password == "":
                curFrame.lb_notice["text"] = "Fields cannot be empty"
                return

            print(username, password)
            login_information = f"{username},{password}"
            sck.sendall(login_information.encode('utf-8'))

            # # Nhận phản hồi từ server
            resp = sck.recv(1024).decode('utf-8')
            if resp == "Successful":
                self.show_page(MainMenu)
                return True
            else:
                curFrame.lb_notice["text"] = "Invalid username/password"
                return False
        except:
            print("Server is not responding")

    def downloadFile(self, curFrame: Frame, sck: socket):
        # Send request for server
        data = "downloadFile"
        sck.sendall(data.encode('utf-8'))

       #Nhan yeu cau nhap duong dan tu sever
        # resp = client.recv(1024).decode('utf-8')
        # resp = curFrame.entry_path.get()
        # sck.sendall(resp.encode("utf-8"))
        # print("Nhap CANCEL de thoat!!!")
        #nhap vao ten file
        # GUI
        msg = curFrame.entry_path.get()
        if msg == 'CANCEL':
            sck.sendall(msg.encode('utf-8'))
            return
        #gui ten file hoac duong dan
        sck.sendall(msg.encode('utf-8'))
        #gui trang thai xem file co ton tai tren sever hay khong
        checkStatus = sck.recv(1024).decode('utf-8')
        if checkStatus == 'Not exist':
            print("File khong ton tai!!!")
            return
        else:
            resp = "Da nhan duoc"
            sck.sendall(resp.encode('utf-8'))
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
        sizeRecv = sck.recv(1024).decode('utf-8')
        size = int(sizeRecv)
        sizeResp = "Nhan thanh cong"
        sck.sendall(sizeResp.encode('utf-8'))
        ofs = open(fileWrite, "wb")
        sw = 0
        while size > sw:
            data = sck.recv(1024)
            if not data:
                break
            ofs.write(data)
            sw += len(data)
        ofs.close()
        sck.sendall(str(sw).encode('utf-8'))
        # respSta = sck.recv(1024).decode('utf-8')
        # sck.sendall("da nhan".encode('utf-8'))
        resp = sck.recv(1024).decode('utf-8')
        if resp == "Success":
            print(f"Sever: Da download file thanh cong. File dang duoc luu tru tai {fileWrite} ")
        else:
            print(f"Sever: Download file that bai. Loi ket noi!")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 12000))
print("Ket noi thanh cong voi sever!!!")
app = App()
app.mainloop()