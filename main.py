# main.py

from ui_app import App

if __name__ == "__main__":
    # Di customtkinter, tema sudah diatur di dalam ui_app.py
    # Kita hanya perlu membuat dan menjalankan instance App
    app = App()
    app.mainloop()