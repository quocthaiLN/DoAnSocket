from tkinter import *

FONT = "JetBrains Mono"

class HomePage(Frame):
    def __init__(self, parent, app_pointer):
        Frame.__init__(self, parent)

        mainLabel = Label(self, text="Home Page", font=(FONT, 25), bg="PaleGreen")
        mainLabel.place(x = 125, y = 200)

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

        # Entry username
        entry_username = Entry(self, width = 25, font = (FONT, 12), bd = 0.25)
        entry_username.place(x = 165, y = 192)
        entry_username.focus()

        # Entry password
        entry_password = Entry(self, width = 25, font = (FONT, 12), bd = 0.25)
        entry_password.place(x = 165, y = 242)

        # Button
        btn_login = Button(self, text = "Sign in", font = (FONT, 9), bg = "#80C4E9", command = lambda: app_pointer.show_page(HomePage))
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
        for F in (LoginPage, HomePage):
            frame = F(container, self)
            frame.grid(row = 0, column = 0, sticky = "nsew")
            self.frames[F] = frame
        
        self.frames[LoginPage].tkraise()

    def show_page(self, class_name):
        self.frames[class_name].tkraise()
        



app = App()
app.mainloop()