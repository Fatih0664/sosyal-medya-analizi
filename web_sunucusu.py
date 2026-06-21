from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "API aktif ve calisiyor!"

# 1. Flutter'ın aradığı ilk link (Trendler)
@app.route('/api/v1/trendler/<kategori>')
def trendleri_getir(kategori):
    ornek_veri = [
        {"icerik": f"{kategori} alaninda yapay zeka patlamasi yasaniyor.", "platform": "X", "duygu_skoru": 0.8, "duygu_durumu": "Pozitif"},
        {"icerik": "Yeni cihazlarin sarj suresi hayal kirikligi.", "platform": "YouTube", "duygu_skoru": -0.6, "duygu_durumu": "Negatif"},
        {"icerik": "Piyasada son durum beklendigi gibi.", "platform": "Facebook", "duygu_skoru": 0.0, "duygu_durumu": "Nötr"},
        {"icerik": "Telegram gruplarinda inanilmaz bir bilgi akisi var.", "platform": "Telegram", "duygu_skoru": 0.5, "duygu_durumu": "Pozitif"}
    ]
    return jsonify(ornek_veri)

# 2. Flutter'ın aradığı ikinci link (Kelime Bulutu)
@app.route('/api/v1/kelime-bulutu/')
def kelime_bulutu():
    ornek_bulut = [
        {"kelime": "YapayZeka", "frekans": 150},
        {"kelime": "Ekonomi", "frekans": 80},
        {"kelime": "Zam", "frekans": 200},
        {"kelime": "Teknoloji", "frekans": 65},
        {"kelime": "Veri", "frekans": 110}
    ]
    return jsonify(ornek_bulut)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
