# database.py

import pyodbc
from fastapi import HTTPException

# --- KENDİ BİLGİLERİNİZİ BURAYA GİRİN ---
SERVER_NAME = r'BEYZ\SQLEXPRESS'  # SQL Server Management Studio'daki sunucu adınız
DATABASE_NAME = 'MusicAppDB'
# -----------------------------------------

# Windows Authentication için bağlantı cümlesi
CONN_STR = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SERVER_NAME};'
    f'DATABASE={DATABASE_NAME};'
    f'Trusted_Connection=yes;'
)

def get_db_connection():
    """
    Veritabanı bağlantısı kurar ve cursor nesnesini döndürür.
    DİKKAT: Bu fonksiyon artık doğrudan kullanılmıyor, yerine aşağıdaki yardımcı fonksiyonlar var.
    """
    try:
        # autocommit=True, her sorgudan sonra veritabanına otomatik olarak kaydetmesini sağlar.
        conn = pyodbc.connect(CONN_STR, autocommit=True)
        return conn.cursor()
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Veritabanı bağlantı hatası: {sqlstate}")
        raise HTTPException(status_code=500, detail="Veritabanı sunucusuna bağlanılamadı.")

# === YENİ YARDIMCI FONKSİYONLAR ===

def execute_query(query: str, params: tuple = ()):
    """
    SELECT sorguları için yardımcı fonksiyon.
    Sonucu bir sözlük listesi olarak döndürür.
    """
    cursor = get_db_connection()
    try:
        cursor.execute(query, params)
        # Sütun isimlerini alarak daha kullanışlı bir sonuç oluştur
        columns = [column[0] for column in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()

def execute_non_query(query: str, params: tuple = ()):
    """
    INSERT, UPDATE, DELETE gibi veri değiştiren sorgular için yardımcı fonksiyon.
    Bir şey döndürmez.
    """
    cursor = get_db_connection()
    try:
        cursor.execute(query, params)
    finally:
        cursor.close()