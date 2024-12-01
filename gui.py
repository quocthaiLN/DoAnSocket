from tkinter import *
import socket

FONT = "JetBrains Mono"
BTN_COLOR = "#A1EEBD"
WIDTH_BTN = 18 # width of featured buttons

class MainMenu(Frame):
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)

        lb_main = Label(self, text = "Main Menu", font = (FONT, 20, "bold"))
        lb_main.pack()

        # Button
        btn_download_file = Button(self, text = "Download file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_download_file.pack()

        btn_download_folder = Button(self, text = "Download folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_download_folder.pack()

        btn_upload_file = Button(self, text = "Upload file", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_upload_file.pack()

        btn_upload_folder = Button(self, text = "Upload folder", font = (FONT, 12), bg = BTN_COLOR, width = WIDTH_BTN)
        btn_upload_folder.pack()

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
        btn_login = Button(self, text = "Sign in", font = (FONT, 9), bg = "#80C4E9", command = lambda: app_pointer.login(self, client))
        btn_login.place(x = 195, y = 290)


class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.title("Application")
        self.geometry("450x550")
        self.resizable(width = False, height = False)
        self.attributes("-topmost", True)
        # self["bg"] = "white"

        container = Frame(self)

        # login_frame = LoginPage(container)
        # home_frame = HomePage(container)

        # Đoạn code dùng nếu muốn thay đổi các frame
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Tạo một dictionary để lưu các class page
        # Dùng vòng for để grid các frame này, thay vì làm tuần tự
        self.frames = {}
        for F in (LoginPage, MainMenu):
            frame = F(container, self)
            frame.grid(row = 0, column = 0, sticky = "nsew")
            self.frames[F] = frame
        
        self.frames[LoginPage].tkraise()

    def show_page(self, class_name):
        self.frames[class_name].tkraise()

    def login(self, curFrame, sck):
        # Nhận yêu cầu từ server để nhập thông tin
        request = client.recv(1024).decode('utf-8')
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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 2810))
print("Ket noi thanh cong voi sever!!!")
app = App()
app.mainloop()