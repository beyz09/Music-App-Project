Kişisel Müzik Arşivi Web Uygulaması
Bu proje, Bartın Üniversitesi Veritabanı Yönetim Sistemleri-II dersi final ödevi kapsamında geliştirilmiştir. Kullanıcıların kendi müzik arşivlerini (sanatçılar, albümler, şarkılar) oluşturup yönetebildiği, çalma listeleri hazırlayabildiği ve yükledikleri müzikleri doğrudan web arayüzü üzerinden dinleyebildiği tam fonksiyonlu bir web uygulamasıdır.
Proje, Python (FastAPI) backend'i ve MS SQL Server veritabanı üzerine kurulmuştur. Arayüz, Jinja2 şablon motoru ve Bootstrap 5 ile sunucu tarafında oluşturulmaktadır.
<!-- Buraya kendi uygulamanızın ekran görüntüsünün linkini koyabilirsiniz -->
Proje Özellikleri
CRUD İşlemleri: Sanatçılar, albümler, şarkılar ve çalma listeleri için Ekleme, Okuma, Güncelleme ve Silme (CRUD) işlevlerinin tamamı.
Dinamik Çalma Listeleri: Var olan şarkıları kolayca çalma listelerine ekleme ve çıkarma.
Medya Yönetimi:
Şarkılar için .mp3 formatında ses dosyası yükleme.
Çalma listeleri için kapak resmi yükleme.
Web Tabanlı Müzik Çalar: HTML5 <audio> elementi ile entegre, basit ve etkili bir müzik çalar.
Teknoloji Mimarisi:
Backend: Python 3.10 ve FastAPI
Frontend: Jinja2 Template Engine ve Bootstrap 5
Veritabanı: Microsoft SQL Server
Veritabanı Etkileşimi: pyodbc kütüphanesi ve Saklı Yordamlar (Stored Procedures)
Kurulum ve Çalıştırma Adımları
Bu projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.
1. Ön Gereksinimler
Python (Sürüm 3.8+): Python'un resmi sitesinden yükleyin.
Microsoft SQL Server: Express Edition (ücretsiz) veya Developer Edition kurun.
SQL Server Management Studio (SSMS): Veritabanını yönetmek için SSMS'i indirin.
Microsoft ODBC Driver for SQL Server: Python'un SQL Server ile konuşabilmesi için gereklidir. Buradan indirin.
2. Projeyi Klonlama
Projeyi bilgisayarınıza indirmek için bir terminal açın ve aşağıdaki komutu çalıştırın:
Generated bash
git clone https://github.com/beyz09/Music-App-Project.git
cd Music-App-Project
Use code with caution.
Bash
3. Veritabanını Kurma
SQL Server Management Studio'yu (SSMS) açın ve sunucunuza bağlanın.
SSMS'de, File > Open > File... menüsünü kullanarak proje klasöründeki setup_database.sql dosyasını açın.
Açılan sorgu ekranında Execute butonuna basın. Bu script, MusicAppDB adında bir veritabanı oluşturacak, tüm tabloları, prosedürleri, fonksiyonları, trigger'ları kuracak ve başlangıç için gerekli temel verileri (sanatçılar, albümler vb.) ekleyecektir.
Önemli Not: Eğer SQL Server'ınızın adı BEYZ\SQLEXPRESS'ten farklıysa, database.py dosyasını açıp SERVER_NAME değişkenini kendi sunucu adınızla güncellemeniz gerekmektedir.
4. Python Ortamını Ayarlama
Projenin ihtiyaç duyduğu Python kütüphanelerini yüklemek en iyi pratik, bir sanal ortam (venv) oluşturmaktır.
Proje ana dizininde bir terminal açın ve aşağıdaki komutlarla sanal ortamı oluşturup aktif hale getirin:
Generated bash
# Sanal ortamı oluştur (sadece bir kez)
python -m venv venv

# Sanal ortamı aktive et
# Windows için:
.\venv\Scripts\activate
# macOS/Linux için:
# source venv/bin/activate
Use code with caution.
Bash
Gerekli paketleri requirements.txt dosyasından yükleyin:
Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
Eğer requirements.txt dosyası yoksa, şu komutla paketleri tek tek yükleyebilirsiniz:
Generated bash
pip install fastapi "uvicorn[standard]" jinja2 pyodbc python-multipart
Use code with caution.
Bash
5. Uygulamayı Başlatma
Sanal ortamın aktif olduğundan emin olduğunuz terminalde, aşağıdaki komutu çalıştırarak web sunucusunu başlatın:
Generated bash
uvicorn main:app --reload
Use code with caution.
Bash
Terminalde Uvicorn running on http://127.0.0.1:8000 mesajını gördüğünüzde, web tarayıcınızı açın ve bu adrese gidin:
http://127.0.0.1:8000
