import requests
import time
import random

# API'mizin adresi
API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

# Simüle edilmiş bot verileri
ornek_veriler = [
    {"platform": "Ekşi Sözlük", "kategori": "Ekonomi", "icerik": "Kiralar yine artmış, bu gidişat hiç iyi değil.", "duygu_durumu": "Negatif 🔴", "duygu_skoru": -0.7},
    {"platform": "TikTok", "kategori": "Sağlık", "icerik": "Günde 3 litre su içmenin cilde faydaları! İnanılmaz değişim.", "duygu_durumu": "Pozitif 🟢", "duygu_skoru": 0.9},
    {"platform": "Telegram", "kategori": "Siyaset", "icerik": "Yeni seçim yasası meclisten geçti, detayları okumak lazım.", "duygu_durumu": "Nötr ⚪", "duygu_skoru": 0.0}
]

print("🤖 Test Botu uyandı. Veriler API'ye gönderiliyor...\n")

for veri in ornek_veriler:
    response = requests.post(API_URL, json=veri)
    if response.status_code == 201:
        print(f"✅ Başarılı! {veri['platform']} verisi merkeze iletildi. (ID: {response.json()['id']})")
    else:
        print(f"❌ Hata: {response.status_code}")
    
    time.sleep(1) # Bot davranışını simüle etmek için 1 saniye bekle

print("\n🎉 Tüm veriler veritabanına işlendi!")