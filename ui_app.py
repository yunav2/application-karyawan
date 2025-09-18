# ui_app.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import database
from datetime import datetime

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Manajemen Karyawan")
        self.geometry("900x600")
        
        self._buat_widgets_utama()
        self.muat_ulang_data()

    def _buat_widgets_utama(self):
        # Frame untuk tombol
        frame_kontrol = ttk.Frame(self)
        frame_kontrol.pack(padx=10, pady=10, fill='x')

        btn_tambah = ttk.Button(frame_kontrol, text="➕ Tambah Karyawan Baru", command=self.buka_form_input)
        btn_tambah.pack(side='left')

        btn_refresh = ttk.Button(frame_kontrol, text="🔄 Refresh Data", command=self.muat_ulang_data)
        btn_refresh.pack(side='left', padx=10)
        
        # Frame untuk tabel
        frame_tabel = ttk.LabelFrame(self, text="Daftar Karyawan")
        frame_tabel.pack(padx=10, pady=10, fill='both', expand=True)

        # Treeview dengan horizontal scrollbar
        columns = ("id_karyawan", "nik", "nama_lengkap", "jabatan", "divisi", "no_hp")
        self.tree = ttk.Treeview(frame_tabel, columns=columns, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar Vertikal dan Horizontal
        vsb = ttk.Scrollbar(frame_tabel, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.pack(fill='x', padx=10, side='bottom')
        self.tree.configure(xscrollcommand=hsb.set)

        # Atur headings
        self.tree.heading("id_karyawan", text="ID")
        self.tree.heading("nik", text="NIK")
        self.tree.heading("nama_lengkap", text="Nama Lengkap")
        self.tree.heading("jabatan", text="Jabatan")
        self.tree.heading("divisi", text="Divisi")
        self.tree.heading("no_hp", text="No. HP")

        # Atur lebar kolom
        self.tree.column("id_karyawan", width=50, stretch=False)
        self.tree.column("nik", width=150, stretch=False)
        self.tree.column("nama_lengkap", width=200)

    def muat_ulang_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = database.ambil_semua_karyawan()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def buka_form_input(self):
        FormInputKaryawan(self)

class FormInputKaryawan(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Form Data Karyawan Baru")
        self.geometry("800x700")
        self.grab_set() # Fokus ke jendela ini

        self.widgets = {}
        self.path_ttd = tk.StringVar()

        # Buat Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Buat Frame untuk setiap tab
        tab_diri = self._buat_tab(notebook, "A. Data Diri")
        tab_kerja = self._buat_tab(notebook, "B. Info Pekerjaan")
        tab_ktp = self._buat_tab(notebook, "C. Kependudukan")
        tab_darurat = self._buat_tab(notebook, "D. Kontak Darurat")
        tab_keluarga = self._buat_tab(notebook, "E. Data Keluarga")
        
        # Tambahkan field ke setiap tab
        self._buat_fields_data_diri(tab_diri)
        self._buat_fields_pekerjaan(tab_kerja)
        self._buat_fields_kependudukan(tab_ktp)
        self._buat_fields_darurat(tab_darurat)
        self._buat_fields_keluarga(tab_keluarga)

        # Tombol Simpan
        btn_simpan = ttk.Button(self, text="Simpan Data Karyawan", command=self.simpan_data)
        btn_simpan.pack(pady=10)

    def _buat_tab(self, notebook, text):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=text)
        return frame
    
    def _buat_field(self, parent, label, row, col, widget_class, **kwargs):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky='w', padx=5, pady=2)
        widget = widget_class(parent, **kwargs)
        widget.grid(row=row, column=col + 1, sticky='ew', padx=5, pady=2)
        return widget
    
    def _buat_fields_data_diri(self, parent):
        self.widgets['nama_lengkap'] = self._buat_field(parent, "Nama Lengkap:", 0, 0, ttk.Entry, width=40)
        self.widgets['nama_panggilan'] = self._buat_field(parent, "Nama Panggilan:", 1, 0, ttk.Entry)
        self.widgets['tempat_lahir'] = self._buat_field(parent, "Tempat Lahir:", 2, 0, ttk.Entry)
        self.widgets['tanggal_lahir'] = self._buat_field(parent, "Tanggal Lahir:", 3, 0, DateEntry, date_pattern='y-mm-dd', width=18)
        self.widgets['jenis_kelamin'] = self._buat_field(parent, "Jenis Kelamin:", 4, 0, ttk.Combobox, values=['Laki-laki', 'Perempuan'], state='readonly')
        self.widgets['gol_darah'] = self._buat_field(parent, "Gol. Darah:", 5, 0, ttk.Entry)
        self.widgets['agama'] = self._buat_field(parent, "Agama:", 6, 0, ttk.Entry)
        self.widgets['tanda_tangan_img'] = self._buat_field(parent, "Tanda Tangan:", 7, 0, ttk.Label, textvariable=self.path_ttd)
        ttk.Button(parent, text="Pilih File...", command=self._pilih_ttd).grid(row=7, column=2, padx=5)
        
    def _buat_fields_pekerjaan(self, parent):
        self.widgets['divisi'] = self._buat_field(parent, "Divisi:", 0, 0, ttk.Entry)
        self.widgets['jabatan'] = self._buat_field(parent, "Jabatan:", 1, 0, ttk.Entry)
        self.widgets['no_rekening'] = self._buat_field(parent, "No. Rekening:", 2, 0, ttk.Entry)
        self.widgets['pendidikan_terakhir'] = self._buat_field(parent, "Pendidikan Terakhir:", 3, 0, ttk.Entry)

    def _buat_fields_kependudukan(self, parent):
        self.widgets['nik'] = self._buat_field(parent, "NIK:", 0, 0, ttk.Entry)
        self.widgets['no_hp'] = self._buat_field(parent, "No. HP:", 1, 0, ttk.Entry)
        self.widgets['status_pernikahan'] = self._buat_field(parent, "Status Pernikahan:", 2, 0, ttk.Combobox, values=['Belum Menikah', 'Menikah', 'Cerai Hidup', 'Cerai Mati'], state='readonly')
        ttk.Label(parent, text="Alamat Sesuai KTP:").grid(row=3, column=0, sticky='nw', padx=5, pady=2)
        self.widgets['alamat_sesuai_ktp'] = tk.Text(parent, height=4, width=40)
        self.widgets['alamat_sesuai_ktp'].grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(parent, text="Alamat Sekarang:").grid(row=4, column=0, sticky='nw', padx=5, pady=2)
        self.widgets['alamat_sekarang'] = tk.Text(parent, height=4, width=40)
        self.widgets['alamat_sekarang'].grid(row=4, column=1, padx=5, pady=2)

    def _buat_fields_darurat(self, parent):
        self.widgets['nama_kontak_darurat'] = self._buat_field(parent, "Nama Kontak Darurat:", 0, 0, ttk.Entry)
        self.widgets['no_telepon_darurat'] = self._buat_field(parent, "No. Telepon Darurat:", 1, 0, ttk.Entry)
        self.widgets['hubungan'] = self._buat_field(parent, "Hubungan:", 2, 0, ttk.Entry)
        ttk.Label(parent, text="Alamat Kontak Darurat:").grid(row=3, column=0, sticky='nw', padx=5, pady=2)
        self.widgets['alamat_darurat'] = tk.Text(parent, height=4, width=40)
        self.widgets['alamat_darurat'].grid(row=3, column=1, padx=5, pady=2)

    def _buat_fields_keluarga(self, parent):
        self.widgets['nama_pasangan'] = self._buat_field(parent, "Nama Pasangan:", 0, 0, ttk.Entry)
        self.widgets['tempat_lahir_pasangan'] = self._buat_field(parent, "Tempat Lahir Pasangan:", 1, 0, ttk.Entry)
        self.widgets['tanggal_lahir_pasangan'] = self._buat_field(parent, "Tgl Lahir Pasangan:", 2, 0, DateEntry, date_pattern='y-mm-dd', width=18)
        
        self.widgets['nama_anak_1'] = self._buat_field(parent, "Nama Anak 1:", 3, 0, ttk.Entry)
        self.widgets['tempat_lahir_anak_1'] = self._buat_field(parent, "Tempat Lahir Anak 1:", 4, 0, ttk.Entry)
        self.widgets['tanggal_lahir_anak_1'] = self._buat_field(parent, "Tgl Lahir Anak 1:", 5, 0, DateEntry, date_pattern='y-mm-dd', width=18)
        
        # ... bisa ditambahkan untuk anak 2 dan 3 dengan cara yang sama ...
        self.widgets['nama_anak_2'] = self._buat_field(parent, "Nama Anak 2:", 6, 0, ttk.Entry)
        self.widgets['tanggal_lahir_anak_2'] = self._buat_field(parent, "Tgl Lahir Anak 2:", 7, 0, DateEntry, date_pattern='y-mm-dd', width=18)
        self.widgets['nama_anak_3'] = self._buat_field(parent, "Nama Anak 3:", 8, 0, ttk.Entry)
        self.widgets['tanggal_lahir_anak_3'] = self._buat_field(parent, "Tgl Lahir Anak 3:", 9, 0, DateEntry, date_pattern='y-mm-dd', width=18)


    def _pilih_ttd(self):
        filepath = filedialog.askopenfilename(
            title="Pilih Gambar Tanda Tangan",
            filetypes=(("Image Files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
        )
        if filepath:
            self.path_ttd.set(filepath)

    def simpan_data(self):
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, (ttk.Entry, ttk.Combobox, DateEntry)):
                value = widget.get()
            elif isinstance(widget, tk.Text):
                value = widget.get("1.0", "end-1c")
            elif isinstance(widget, ttk.Label):
                value = self.path_ttd.get()
            else:
                value = None
            
            # Jika value kosong, ganti dengan None agar sesuai dengan database (terutama untuk tanggal)
            data[key] = value if value else None
        
        # Hitung Usia
        if data['tanggal_lahir']:
            today = datetime.today()
            birth_date = datetime.strptime(data['tanggal_lahir'], '%Y-%m-%d')
            data['usia'] = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        else:
            data['usia'] = None
        
        # Menambahkan kolom anak yang tidak dibuat fieldnya
        for col in ['tempat_lahir_anak_2', 'tempat_lahir_anak_3']:
            if col not in data:
                data[col] = None

        hasil = database.tambah_karyawan(data)
        if hasil is True:
            messagebox.showinfo("Sukses", "Data karyawan berhasil disimpan!", parent=self)
            self.destroy() # Tutup form
            self.parent.muat_ulang_data() # Refresh tabel di jendela utama
        else:
            messagebox.showerror("Error", f"Gagal menyimpan data:\n{hasil}", parent=self)