# ui_app.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
import tkinter as tk
from tkinter import messagebox, filedialog, W
import database
from config import DB_CONFIG
from datetime import datetime

class App(ttk.Window):
    def __init__(self, **kwargs):
        super().__init__(themename="litera", **kwargs)
        
        self.app_style = ttk.Style()
        self.app_style.configure('TLabel', font=('Calibri', 12))
        self.app_style.configure('TButton', font=('Calibri', 12))
        self.app_style.configure('TEntry', font=('Calibri', 12))
        self.app_style.configure('TCombobox', font=('Calibri', 12))
        self.app_style.configure('TLabelframe.Label', font=('Calibri', 12, 'bold'))
        
        self.db_config = DB_CONFIG 
        self.update_title()
        self.geometry("1100x700")
        
        self._buat_menu()
        self._buat_widgets_utama()
        self.inisialisasi_awal()
        
    def inisialisasi_awal(self):
        sukses, pesan = database.tes_koneksi(self.db_config)
        if sukses:
            database.init_db(self.db_config)
            self.muat_ulang_data()
        else:
            messagebox.showerror("Koneksi Awal Gagal", pesan)

    def update_title(self):
        db_name = self.db_config.get('database', 'Unknown')
        host_name = self.db_config.get('host', 'Unknown')
        self.title(f"Sistem Manajemen Karyawan - ({db_name} on {host_name})")

    def _buat_menu(self):
        menu_bar = tk.Menu(self)
        self.configure(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Ganti Koneksi Database...", command=self.buka_dialog_koneksi)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.quit)

    def _buat_widgets_utama(self):
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill=BOTH, expand=True)
        kontrol_frame = ttk.Frame(main_frame)
        kontrol_frame.pack(fill=X, pady=(0, 15))
        btn_tambah = ttk.Button(kontrol_frame, text="➕ Tambah Karyawan", command=self.buka_form_input, bootstyle="success")
        btn_tambah.pack(side=LEFT, padx=(0, 10))
        btn_refresh = ttk.Button(kontrol_frame, text="🔄 Refresh", command=self.muat_ulang_data, bootstyle="info")
        btn_refresh.pack(side=LEFT)
        search_frame = ttk.Frame(kontrol_frame)
        search_frame.pack(side=RIGHT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=(0, 5))
        self.search_entry.insert(0, "🔍 Ketik untuk mencari...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete('0', 'end') if self.search_entry.get() == "🔍 Ketik untuk mencari..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "🔍 Ketik untuk mencari...") if not self.search_entry.get() else None)
        self.search_entry.bind("<KeyRelease>", self._cari_data)
        tabel_frame = ttk.LabelFrame(main_frame, text="Daftar Karyawan")
        tabel_frame.pack(fill=BOTH, expand=True)
        columns = ("id_karyawan", "nik", "nama_lengkap", "jabatan", "divisi", "no_hp")
        self.tree = ttk.Treeview(tabel_frame, columns=columns, show="headings", bootstyle="secondary")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.app_style.configure("Treeview", rowheight=30, font=('Calibri', 12))
        self.app_style.configure("Treeview.Heading", font=('Calibri', 13, 'bold'))
        vsb = ttk.Scrollbar(tabel_frame, orient="vertical", command=self.tree.yview, bootstyle="round")
        vsb.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=vsb.set)
        headings = {"id_karyawan": "ID", "nik": "NIK", "nama_lengkap": "Nama Lengkap", "jabatan": "Jabatan", "divisi": "Divisi", "no_hp": "No. HP"}
        for col, text in headings.items():
            self.tree.heading(col, text=text, anchor=W)
        self.tree.column("id_karyawan", width=50, stretch=False)
            
    def muat_ulang_data(self):
        self.semua_data = database.ambil_semua_karyawan(self.db_config)
        self._tampilkan_di_treeview(self.semua_data)
        
    def _cari_data(self, event=None):
        query = self.search_entry.get().lower()
        if not hasattr(self, 'semua_data') or not self.semua_data: return
        hasil_filter = [row for row in self.semua_data if any(query in str(val).lower() for val in row)]
        self._tampilkan_di_treeview(hasil_filter)

    def _tampilkan_di_treeview(self, data_list):
        self.tree.delete(*self.tree.get_children())
        for row in data_list:
            self.tree.insert("", "end", values=row)

    def buka_dialog_koneksi(self):
        DialogKoneksi(self, self.db_config, self.update_koneksi_dan_refresh)
    
    def update_koneksi_dan_refresh(self, new_config):
        self.db_config = new_config
        self.update_title()
        self.muat_ulang_data()
        messagebox.showinfo("Sukses", f"Berhasil terhubung ke database '{new_config['database']}'!")

    def buka_form_input(self):
        FormInputKaryawan(self, self.db_config)

class DialogKoneksi(ttk.Toplevel):
    def __init__(self, parent, current_config, callback):
        super().__init__(parent)
        self.title("Ganti Koneksi Database")
        self.parent = parent
        self.callback = callback
        
        frame = ttk.Frame(self, padding="15")
        frame.pack(fill="both", expand=True)
        fields = ['host', 'user', 'password', 'database']
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field.title()}:").grid(row=i, column=0, sticky='w', padx=5, pady=8)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=8)
            entry.insert(0, current_config.get(field, ''))
            self.entries[field] = entry
        
        btn_frame = ttk.Frame(self, padding=(0, 10))
        btn_frame.pack()
        btn_test = ttk.Button(btn_frame, text="Tes Koneksi", command=self._tes_koneksi, bootstyle="info-outline")
        btn_test.pack(side="left", padx=5)
        btn_save = ttk.Button(btn_frame, text="Simpan & Hubungkan", command=self._simpan, bootstyle="primary")
        btn_save.pack(side="left", padx=5)
        self.grab_set()

    def _get_current_config(self):
        return {key: entry.get() for key, entry in self.entries.items()}
    def _tes_koneksi(self):
        config = self._get_current_config()
        sukses, pesan = database.tes_koneksi(config)
        if sukses: messagebox.showinfo("Sukses", pesan, parent=self)
        else: messagebox.showerror("Gagal", pesan, parent=self)
    def _simpan(self):
        new_config = self._get_current_config()
        sukses, pesan = database.tes_koneksi(new_config)
        if sukses:
            self.callback(new_config)
            self.destroy()
        else: messagebox.showerror("Gagal", f"Tidak dapat menyimpan. {pesan}", parent=self)

class FormInputKaryawan(ttk.Toplevel):
    def __init__(self, parent, db_config):
        super().__init__(parent)
        self.parent = parent
        self.db_config = db_config
        self.title("Form Data Karyawan Baru")
        self.geometry("900x700")
        self.resizable(False, False)
        self.grab_set()

        self.widgets = {}
        
        button_frame = ttk.Frame(self, padding=(10, 15))
        button_frame.pack(side=BOTTOM, fill=X)
        button_frame.columnconfigure((0,1), weight=1)
        btn_batal = ttk.Button(button_frame, text="Batal", command=self.destroy, bootstyle="secondary")
        btn_batal.grid(row=0, column=0, sticky=EW, padx=(0,5))
        btn_simpan = ttk.Button(button_frame, text="Simpan Data Karyawan", command=self.simpan_data, bootstyle="success")
        btn_simpan.grid(row=0, column=1, sticky=EW, padx=(5,0))
        
        notebook = ttk.Notebook(self, bootstyle="primary")
        notebook.pack(padx=10, pady=(10,0), fill="both", expand=True)

        tab_diri = self._buat_tab(notebook, "A. Data Diri")
        tab_kerja = self._buat_tab(notebook, "B. Info Pekerjaan")
        tab_ktp = self._buat_tab(notebook, "C. Kependudukan")
        tab_darurat = self._buat_tab(notebook, "D. Kontak Darurat")
        tab_keluarga = self._buat_tab(notebook, "E. Data Keluarga")
        
        self._buat_fields_data_diri(tab_diri)
        self._buat_fields_pekerjaan(tab_kerja)
        self._buat_fields_kependudukan(tab_ktp)
        self._buat_fields_darurat(tab_darurat)
        self._buat_fields_keluarga(tab_keluarga)

    def _buat_tab(self, notebook, text):
        frame = ttk.Frame(notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        notebook.add(frame, text=text)
        return frame
    
    def _buat_field(self, parent, key, label, row, widget_class, **kwargs):
        label_widget = ttk.Label(parent, text=label, anchor="w")
        label_widget.grid(row=row, column=0, padx=5, pady=8, sticky="w")
        
        widget = widget_class(parent, **kwargs)
            
        widget.grid(row=row, column=1, padx=5, pady=8, sticky="ew")
        self.widgets[key] = widget
        return widget

    def _update_usia(self, event=None):
        try:
            birth_date = self.widgets['tanggal_lahir'].entry.get_date()
            today = datetime.today().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            self.widgets['usia'].config(state='normal')
            self.widgets['usia'].delete(0, "end"); self.widgets['usia'].insert(0, str(age))
            self.widgets['usia'].config(state='readonly')
        except (ValueError, KeyError, AttributeError):
            if 'usia' in self.widgets: 
                self.widgets['usia'].config(state='normal')
                self.widgets['usia'].delete(0, "end")
                self.widgets['usia'].config(state='readonly')
    
    def _buat_fields_data_diri(self, parent):
        self._buat_field(parent, 'nama_lengkap', "Nama Lengkap:", 0, ttk.Entry)
        self._buat_field(parent, 'nama_panggilan', "Nama Panggilan:", 1, ttk.Entry)
        self._buat_field(parent, 'tempat_lahir', "Tempat Lahir:", 2, ttk.Entry)
        # --- PERBAIKAN: Hapus textvariable yang menyebabkan error ---
        self.widgets['tanggal_lahir'] = self._buat_field(parent, 'tanggal_lahir', "Tanggal Lahir:", 3, DateEntry, dateformat='%Y-%m-%d')
        self.widgets['tanggal_lahir'].entry.bind("<<DateEntrySelected>>", self._update_usia)
        self._buat_field(parent, 'usia', "Usia (otomatis):", 4, ttk.Entry, state="readonly")
        self._buat_field(parent, 'jenis_kelamin', "Jenis Kelamin:", 5, ttk.Combobox, values=['Laki-laki', 'Perempuan'], state='readonly')
        self._buat_field(parent, 'gol_darah', "Gol. Darah:", 6, ttk.Entry)
        self._buat_field(parent, 'agama', "Agama:", 7, ttk.Entry)
        self._buat_field(parent, 'tanda_tangan_img', "Path Tanda Tangan:", 8, ttk.Entry, state="readonly")

    def _buat_fields_pekerjaan(self, parent):
        self._buat_field(parent, 'divisi', "Divisi:", 0, ttk.Entry)
        self._buat_field(parent, 'jabatan', "Jabatan:", 1, ttk.Entry)
        self._buat_field(parent, 'no_rekening', "No. Rekening:", 2, ttk.Entry)
        self._buat_field(parent, 'pendidikan_terakhir', "Pendidikan Terakhir:", 3, ttk.Entry)

    def _buat_fields_kependudukan(self, parent):
        self._buat_field(parent, 'nik', "NIK:", 0, ttk.Entry)
        self._buat_field(parent, 'no_hp', "No. HP:", 1, ttk.Entry)
        self._buat_field(parent, 'status_pernikahan', "Status Pernikahan:", 2, ttk.Combobox, values=['Belum Menikah', 'Menikah', 'Cerai Hidup', 'Cerai Mati'], state='readonly')
        self.widgets['alamat_sesuai_ktp'] = self._buat_field(parent, 'alamat_sesuai_ktp', "Alamat Sesuai KTP:", 3, ttk.Text, height=4)
        self.widgets['alamat_sekarang'] = self._buat_field(parent, 'alamat_sekarang', "Alamat Sekarang:", 4, ttk.Text, height=4)

    def _buat_fields_darurat(self, parent):
        self._buat_field(parent, 'nama_kontak_darurat', "Nama Kontak Darurat:", 0, ttk.Entry)
        self._buat_field(parent, 'no_telepon_darurat', "No. Telepon Darurat:", 1, ttk.Entry)
        self._buat_field(parent, 'hubungan', "Hubungan:", 2, ttk.Entry)
        self.widgets['alamat_darurat'] = self._buat_field(parent, 'alamat_darurat', "Alamat Kontak Darurat:", 3, ttk.Text, height=4)

    def _buat_fields_keluarga(self, parent):
        self._buat_field(parent, 'nama_pasangan', "Nama Pasangan:", 0, ttk.Entry)
        self._buat_field(parent, 'tempat_lahir_pasangan', "Tempat Lahir Pasangan:", 1, ttk.Entry)
        self._buat_field(parent, 'tanggal_lahir_pasangan', "Tgl Lahir Pasangan:", 2, DateEntry)
        ttk.Label(parent, text=" ").grid(row=3, column=0)
        self._buat_field(parent, 'nama_anak_1', "Nama Anak 1:", 4, ttk.Entry)
        self._buat_field(parent, 'tempat_lahir_anak_1', "Tempat Lahir Anak 1:", 5, ttk.Entry)
        self._buat_field(parent, 'tanggal_lahir_anak_1', "Tgl Lahir Anak 1:", 6, DateEntry)
        
    def simpan_data(self):
        data = {}
        for key, widget in self.widgets.items():
            value = ''
            if isinstance(widget, DateEntry):
                try: value = widget.entry.get_date().strftime('%Y-%m-%d')
                except (ValueError, AttributeError): value = None
            elif isinstance(widget, (ttk.Entry, ttk.Combobox)):
                value = widget.get()
            elif isinstance(widget, ttk.Text):
                value = widget.get("1.0", "end-1c")
            data[key] = value if value else None
        
        data['usia'] = self.widgets['usia'].get() if self.widgets['usia'].get() else None
        all_db_keys = ['nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir', 'usia', 'jenis_kelamin', 'gol_darah', 'agama', 'divisi', 'jabatan', 'no_rekening', 'pendidikan_terakhir', 'nik', 'alamat_sesuai_ktp', 'alamat_sekarang', 'no_hp', 'status_pernikahan', 'nama_kontak_darurat', 'no_telepon_darurat', 'hubungan', 'alamat_darurat', 'nama_pasangan', 'tempat_lahir_pasangan', 'tanggal_lahir_pasangan', 'nama_anak_1', 'tempat_lahir_anak_1', 'tanggal_lahir_anak_1', 'nama_anak_2', 'tempat_lahir_anak_2', 'tanggal_lahir_anak_2', 'nama_anak_3', 'tempat_lahir_anak_3', 'tanggal_lahir_anak_3', 'tanda_tangan_img']
        final_data = {key: data.get(key) for key in all_db_keys}
        
        hasil = database.tambah_karyawan(final_data, self.db_config)
        if hasil is True:
            messagebox.showinfo("Sukses", "Data karyawan berhasil disimpan!", parent=self)
            self.destroy()
            self.parent.muat_ulang_data()
        else:
            messagebox.showerror("Error", f"Gagal menyimpan data:\n{hasil}", parent=self)