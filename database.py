# database.py

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG # Mengimpor konfigurasi default

def get_db_connection(db_config):
    """
    Membuat koneksi ke database berdasarkan kamus konfigurasi (db_config) yang diberikan.
    Mengembalikan objek koneksi jika berhasil, atau None jika gagal.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error:
        # Error tidak ditampilkan di sini agar bisa ditangani oleh UI
        return None

def tes_koneksi(db_config):
    """
    Mencoba melakukan koneksi ke database untuk memverifikasi detail koneksi.
    Mengembalikan tuple (boolean, pesan_status).
    """
    conn = get_db_connection(db_config)
    if conn and conn.is_connected():
        conn.close()
        return (True, "Koneksi berhasil!")
    else:
        return (False, "Koneksi Gagal. Periksa kembali detail koneksi Anda.")

def init_db(db_config):
    """
    Memastikan tabel 'karyawan' ada dan memiliki semua kolom yang diperlukan.
    Fungsi ini aman untuk dijalankan setiap kali aplikasi dimulai.
    """
    conn = get_db_connection(db_config)
    if conn is None: 
        print("Inisialisasi DB Gagal: Tidak dapat terhubung ke database.")
        return

    try:
        cursor = conn.cursor()
        
        # Perintah dasar untuk membuat tabel jika belum ada sama sekali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                id_karyawan INT AUTO_INCREMENT PRIMARY KEY,
                nama_lengkap VARCHAR(255) NOT NULL,
                nik VARCHAR(16) NOT NULL UNIQUE
            )
        ''')

        # Kamus yang mendefinisikan skema tabel yang seharusnya
        required_columns = {
            'nama_panggilan': 'VARCHAR(50)', 'tempat_lahir': 'VARCHAR(100) NOT NULL',
            'tanggal_lahir': 'DATE NOT NULL', 'usia': 'TINYINT UNSIGNED',
            'jenis_kelamin': "ENUM('Laki-laki', 'Perempuan') NOT NULL", 'gol_darah': 'VARCHAR(3)',
            'agama': 'VARCHAR(50)', 'divisi': 'VARCHAR(100) NOT NULL',
            'jabatan': 'VARCHAR(100) NOT NULL', 'no_rekening': 'VARCHAR(50) NOT NULL',
            'pendidikan_terakhir': 'VARCHAR(100)', 'alamat_sesuai_ktp': 'TEXT',
            'alamat_sekarang': 'TEXT NOT NULL', 'no_hp': 'VARCHAR(20) NOT NULL',
            'status_pernikahan': "ENUM('Belum Menikah', 'Menikah', 'Cerai Hidup', 'Cerai Mati') NOT NULL",
            'nama_kontak_darurat': 'VARCHAR(255) NOT NULL', 'no_telepon_darurat': 'VARCHAR(20) NOT NULL',
            'hubungan': 'VARCHAR(50) NOT NULL', 'alamat_darurat': 'TEXT',
            'nama_pasangan': 'VARCHAR(255)', 'tempat_lahir_pasangan': 'VARCHAR(100)',
            'tanggal_lahir_pasangan': 'DATE', 'nama_anak_1': 'VARCHAR(255)',
            'tempat_lahir_anak_1': 'VARCHAR(100)', 'tanggal_lahir_anak_1': 'DATE',
            'nama_anak_2': 'VARCHAR(255)', 'tempat_lahir_anak_2': 'VARCHAR(100)',
            'tanggal_lahir_anak_2': 'DATE', 'nama_anak_3': 'VARCHAR(255)',
            'tempat_lahir_anak_3': 'VARCHAR(100)', 'tanggal_lahir_anak_3': 'DATE',
            'tanda_tangan_img': 'VARCHAR(255)'
        }

        # Dapatkan daftar kolom yang sudah ada di database
        cursor.execute("SHOW COLUMNS FROM karyawan")
        existing_columns = [column[0] for column in cursor.fetchall()]
        
        # Bandingkan dan tambahkan kolom yang hilang
        for col_name, col_definition in required_columns.items():
            if col_name not in existing_columns:
                print(f"Menambahkan kolom yang hilang: {col_name}")
                cursor.execute(f"ALTER TABLE karyawan ADD COLUMN {col_name} {col_definition}")
        
        conn.commit()
    except Error as e:
        print(f"Error saat inisialisasi database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def tambah_karyawan(data, db_config):
    """
    Menyimpan data karyawan baru ke dalam database.
    Parameter 'data' adalah sebuah kamus yang key-nya sesuai dengan nama kolom.
    """
    # Urutan kolom ini HARUS dijaga agar sesuai dengan urutan nilai saat eksekusi
    columns = [
        'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir', 'usia',
        'jenis_kelamin', 'gol_darah', 'agama', 'divisi', 'jabatan', 'no_rekening',
        'pendidikan_terakhir', 'nik', 'alamat_sesuai_ktp', 'alamat_sekarang', 'no_hp',
        'status_pernikahan', 'nama_kontak_darurat', 'no_telepon_darurat', 'hubungan',
        'alamat_darurat', 'nama_pasangan', 'tempat_lahir_pasangan', 'tanggal_lahir_pasangan',
        'nama_anak_1', 'tempat_lahir_anak_1', 'tanggal_lahir_anak_1',
        'nama_anak_2', 'tempat_lahir_anak_2', 'tanggal_lahir_anak_2',
        'nama_anak_3', 'tempat_lahir_anak_3', 'tanggal_lahir_anak_3', 'tanda_tangan_img'
    ]
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO karyawan ({', '.join(columns)}) VALUES ({placeholders})"
    
    conn = get_db_connection(db_config)
    if conn is None: 
        return "Koneksi ke database gagal."
        
    try:
        cursor = conn.cursor()
        # Membuat tuple nilai yang urutannya sesuai dengan daftar 'columns'
        data_values = tuple(data.get(col) for col in columns)
        cursor.execute(query, data_values)
        conn.commit()
        return True
    except Error as e:
        print(f"Error saat memasukkan data: {e}")
        return str(e) # Mengembalikan pesan error untuk ditampilkan di UI
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def ambil_semua_karyawan(db_config):
    """
    Mengambil data ringkas semua karyawan untuk ditampilkan di tabel utama.
    Mengembalikan daftar (list) dari tuple.
    """
    query = "SELECT id_karyawan, nik, nama_lengkap, jabatan, divisi, no_hp FROM karyawan ORDER BY nama_lengkap"
    conn = get_db_connection(db_config)
    if conn is None: 
        return []

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error saat mengambil data: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()