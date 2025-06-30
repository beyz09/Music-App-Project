# Kişisel Müzik Arşivi

FastAPI ve SQL Server kullanılarak oluşturulmuş, kişisel müziklerinizi yönetebileceğiniz ve çalma listeleri oluşturabileceğiniz bir web uygulamasıdır.

## 🚀 Teknoloji Stack'i
- **Backend**: FastAPI
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Veritabanı**: Microsoft SQL Server
- **Python Sürümü**: 3.9+

## 🛠️ Kurulum Adımları

Bu projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlama
Öncelikle, projeyi GitHub'dan yerel makinenize klonlayın:
```bash
git clone https://github.com/beyz09/Music-App-Project.git
cd Music-App-Project
```

### 2. Python Sanal Ortamı
Proje kök dizinindeyken bir sanal ortam oluşturun ve aktive edin:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Gerekli Paketlerin Yüklenmesi
Projenin ihtiyaç duyduğu Python paketlerini `requirements.txt` dosyasını kullanarak yükleyin:
```bash
pip install -r requirements.txt
```
### 4. Veritabanı Kurulumu

Bu proje, Microsoft SQL Server veritabanı kullanmaktadır.

**a. Bağlantı Ayarları:**
`database.py` dosyasını açın ve kendi SQL Server bilgilerinizi girin:
```python
# database.py

# --- KENDİ BİLGİLERİNİZİ BURAYA GİRİN ---
SERVER_NAME = r'SUNUCU_ADINIZ\SQLEXPRESS'  # SQL Server Management Studio'daki sunucu adınız
DATABASE_NAME = 'MusicAppDB' # Oluşturacağınız veritabanı adı
# -----------------------------------------
```
sql scriptimin tamamı da proje klasörünün içerisinde -> music_web_app.sql


### 5. Uygulamayı Çalıştırma
Tüm kurulum adımları tamamlandıktan sonra, FastAPI uygulamasını Uvicorn ile başlatabilirsiniz:
```bash
uvicorn main:app --reload
```
Uygulama `http://127.0.0.1:8000` adresinde çalışıyor olacaktır.
