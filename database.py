# database.py

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_db_connection():
    """Membuat dan mengembalikan objek koneksi database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def init_db():
    """Membuat tabel dan kolom yang diperlukan sesuai skema baru."""
    conn = get_db_connection()
    if conn is None: return

    try:
        cursor = conn.cursor()
        
        # Sintaks CREATE TABLE utama
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                id_karyawan INT AUTO_INCREMENT PRIMARY KEY,
                nama_lengkap VARCHAR(255) NOT NULL,
                nik VARCHAR(16) NOT NULL UNIQUE
            )
        ''')

        # Definisi semua kolom yang dibutuhkan
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

        # Periksa dan tambahkan kolom yang hilang
        cursor.execute("SHOW COLUMNS FROM karyawan")
        existing_columns = [column[0] for column in cursor.fetchall()]
        
        for col_name, col_definition in required_columns.items():
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE karyawan ADD COLUMN {col_name} {col_definition}")
        
        conn.commit()
    except Error as e:
        print(f"Error during DB initialization: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def tambah_karyawan(data):
    """Menyimpan data karyawan baru dengan semua kolom."""
    # Pastikan urutan kolom sesuai dengan urutan nilai di tuple 'data_values'
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
    
    conn = get_db_connection()
    if conn is None: return False
    
    try:
        cursor = conn.cursor()
        data_values = tuple(data[col] for col in columns) # Ambil nilai sesuai urutan kolom
        cursor.execute(query, data_values)
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting data: {e}")
        return str(e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def ambil_semua_karyawan():
    """Mengambil data ringkas karyawan untuk ditampilkan di tabel utama."""
    query = "SELECT id_karyawan, nik, nama_lengkap, jabatan, divisi, no_hp FROM karyawan ORDER BY nama_lengkap"
    conn = get_db_connection()
    if conn is None: return []

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error fetching data: {e}")
        return []