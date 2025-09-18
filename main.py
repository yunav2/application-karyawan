# main.py

import database
from ui_app import App

if __name__ == "__main__":
    # Pastikan database dan tabel sudah siap sebelum aplikasi jalan
    database.init_db()
    
    # Membuat instance aplikasi dan menjalankannya
    app = App()
    app.mainloop()

