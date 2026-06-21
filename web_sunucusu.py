from flask import Flask, jsonify
import sqlite3
import re
from collections import Counter

app = Flask(__name__)

# Doğru veritabanı dosyası
VERITABANI_ADI = 'turkiye_veri_agi.db' 

def db_baglantisi():
    conn = sqlite3.connect(VERITABANI_ADI)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "API aktif ve gerçek verilerle calisiyor!"

# 1. Gerçek Trend Verilerini Çeken Uç
@app.route('/api/v1/trendler/<kategori>')
def trendleri_getir(kategori):
    try:
        conn = db_baglantisi()
        cursor = conn.cursor()
        
        # Tablo adı doğru şekilde sosyal_medya_akis olarak ayarlandı
        cursor.execute("""
            SELECT icerik, platform, duygu_skoru, duygu_durumu 
            FROM sosyal_medya_akis 
            ORDER BY id DESC LIMIT 50
        """)
        satirlar = cursor.fetchall()
        conn.close()

        gercek_veri = []
        for satir in satirlar:
            gercek_veri.append({
                "icerik": satir["icerik"],
                "platform": satir["platform"],
                "duygu_skoru": satir["duygu_skoru"],
                "duygu_durumu": satir["duygu_durumu"]
            })
            
        return jsonify(gercek_veri)
    except Exception as e:
        return jsonify([{"icerik": f"Veritabanı Hatası: {str(e)}", "platform": "Sistem", "duygu_skoru": 0.0, "duygu_durumu": "Nötr"}])

# 2. Gerçek Kelime Bulutu Üreten Uç
@app.route('/api/v1/kelime-bulutu/')
def kelime_bulutu():
    try:
        conn = db_baglantisi()
        cursor = conn.cursor()
        # Kelime bulutu için de doğru tabloya bağlanıyoruz
        cursor.execute("SELECT icerik FROM sosyal_medya_akis LIMIT 100")
        satirlar = cursor.fetchall()
        conn.close()

        # Boş içerikleri filtreleyip metinleri birleştiriyoruz
        tum_metin = " ".join([satir["icerik"] for satir in satirlar if satir["icerik"]]).lower()
        
        kelimeler = re.findall(r'\b[a-zçğıöşü]+\b', tum_metin)
        cop_kelimeler = {"bir", "ve", "bu", "da", "de", "icin", "ile", "cok", "gibi", "daha", "en", "var", "yok"}
        temiz_kelimeler = [k for k in kelimeler if k not in cop_kelimeler and len(k) > 2]

        frekanslar = Counter(temiz_kelimeler).most_common(15)
        gercek_bulut = [{"kelime": k.capitalize(), "frekans": f} for k, f in frekanslar]
        
        return jsonify(gercek_bulut)
    except Exception as e:
        return jsonify([{"kelime": "Hata", "frekans": 100}])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
