import os
import time
import random
import threading
from queue import Queue
from datetime import datetime
from supabase import create_client
from ddgs import DDGS
from flask import Flask

# --- FLASK WEB SUNUCUSU AYARLARI ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🟢 MEGA KAZIYICI BOT AYAKTA! Veri toplamaya devam ediyor..."

# --- SUPABASE AYARLARI ---
SUPABASE_URL = "https://oskhluimvjvjhbtjqnoo.supabase.co"
SUPABASE_KEY = "sb_secret_MsMqFI2v9VF68mf6MyKhTg_wLLrlTky"

os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_KEY"] = SUPABASE_KEY

PROXY_LISTESI = []

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Bulut veritabanı bağlantısı başarıyla kuruldu!")
except Exception as e:
    print(f"⚠️ Bağlantı hatası (Yine de devam edilecek): {e}")

def hizli_duygu_analizi(metin):
    metin = str(metin).lower()
    pozitif_kelimeler = ['iyi', 'güzel', 'harika', 'başarılı', 'süper', 'muhteşem', 'artış', 'büyüme', 'kâr', 'fırsat', 'çözüm', 'destek', 'seviyorum', 'tebrik']
    negatif_kelimeler = ['kötü', 'berbat', 'sorun', 'hata', 'kriz', 'düşüş', 'zarar', 'zam', 'enflasyon', 'işsizlik', 'felaket', 'çöküş', 'şikayet', 'nefret']
    
    pozitif_skor = sum(1 for kelime in pozitif_kelimeler if kelime in metin)
    negatif_skor = sum(1 for kelime in negatif_kelimeler if kelime in metin)
    
    if pozitif_skor > negatif_skor:
        skor = round(random.uniform(0.1, 1.0), 2)
        durum = "Pozitif 🟢"
    elif negatif_skor > pozitif_skor:
        skor = round(random.uniform(-1.0, -0.1), 2)
        durum = "Negatif 🔴"
    else:
        skor = round(random.uniform(-0.1, 0.1), 2)
        durum = "Nötr ⚪"
        
    return skor, durum

def veritabanina_yaz(platform_adi, kategori, icerik, anahtar_kelime):
    duygu_skoru, duygu_durumu = hizli_duygu_analizi(icerik)
    
    veri = {
        "platform": platform_adi,
        "kategori": kategori,
        "icerik": icerik,
        "duygu_skoru": duygu_skoru,
        "duygu_durumu": duygu_durumu,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        supabase.table("sosyal_medya_akis").insert(veri).execute()
        print(f"✅ [KAYDEDİLDİ] Platform: {platform_adi} | Skor: {duygu_skoru}")
    except Exception as e:
        print(f"❌ [HATA - VERİTABANI] Veri kaydedilemedi: {e}")

# --- GERÇEK HEDEF PLATFORMLAR ---
DOMAIN_ESLESME = {
    "Google": ["google.com"],
    "Bing": ["bing.com"],
    "Yahoo": ["yahoo.com"],
    "Facebook": ["facebook.com"],
    "YouTube": ["youtube.com"],
    "WhatsApp": ["whatsapp.com", "wa.me"],
    "X (Twitter)": ["twitter.com", "x.com"],
    "Telegram": ["t.me", "telegram.org"],
    "Instagram": ["instagram.com"],
    "TikTok": ["tiktok.com"]
}

def platform_kaziyici_islem(worker_id, kuyruk):
    print(f"🚀 [Worker-{worker_id}] göreve başladı. Kuyruktan iş bekleniyor...")
    
    while True:
        if not kuyruk.empty():
            gorev = kuyruk.get()
            anahtar_kelime = gorev['kelime']
            platform_adi = gorev['platform']
            kategori = gorev['kategori']
            
            print(f"🔍 [Worker-{worker_id}] Aranıyor: {platform_adi} -> '{anahtar_kelime}'")
            
            try:
                ddgs_kwargs = {}
                if PROXY_LISTESI:
                    ddgs_kwargs['proxy'] = random.choice(PROXY_LISTESI)
                
                with DDGS(**ddgs_kwargs) as ddgs:
                    hedef_domain = DOMAIN_ESLESME.get(platform_adi, [platform_adi.lower()])[0]
                    arama_sorgusu = f"{anahtar_kelime} site:{hedef_domain}"
                    
                    sonuclar = list(ddgs.text(arama_sorgusu, max_results=15))
                    
                    if not sonuclar:
                        print(f"🛑 [Worker-{worker_id}] 0 Sonuç!")
                    else:
                        bulunan_sayi = 0
                        gecerli_domainler = DOMAIN_ESLESME.get(platform_adi, [platform_adi.lower()])
                        
                        for sonuc in sonuclar:
                            icerik = f"{sonuc.get('title', '')} - {sonuc.get('body', '')}"
                            href = str(sonuc.get('href', '')).lower()
                            domain_dogru_mu = any(dom in href for dom in gecerli_domainler)
                            
                            if len(icerik) > 20 and domain_dogru_mu: 
                                veritabanina_yaz(platform_adi, kategori, icerik, anahtar_kelime)
                                bulunan_sayi += 1
                                
                        print(f"🎯 [Worker-{worker_id}] GÖREV BİTTİ: '{anahtar_kelime}' -> {bulunan_sayi} adet veri çekildi.")
                    
            except Exception as e:
                print(f"⚠️ [Worker-{worker_id}] BAĞLANTI HATASI: {e}")
            
            time.sleep(random.uniform(8.0, 15.0))
        else:
            time.sleep(3)

def bot_yoneticisi():
    gorev_kuyrugu = Queue()
    
    aranacak_sorgular = [
        {"kelime": "işsizlik kriz", "kategori": "Genel Ekonomi 💰"},
        {"kelime": "bitcoin kripto", "kategori": "Kripto & Finans 🪙"},
        {"kelime": "yapay zeka yazılım", "kategori": "Yapay Zeka (AI) 🤖"},
        {"kelime": "hastane doktor randevu", "kategori": "Sağlık & Psikoloji 🏥"},
        {"kelime": "seçim meclis muhalefet", "kategori": "Siyaset 🏛️"},
        {"kelime": "savaş silah ordu", "kategori": "Savunma & Çatışma ⚔️"},
        {"kelime": "iklim deprem sel", "kategori": "İklim & Çevre 🌍"},
        {"kelime": "üniversite eğitim sınav", "kategori": "Eğitim 📚"}
    ]
    
    hedef_platformlar = [
        "Google", "Bing", "Yahoo", "Facebook", "YouTube", 
        "WhatsApp", "X (Twitter)", "Telegram", "Instagram", "TikTok"
    ]
    
    while True:
        for platform in hedef_platformlar:
            for sorgu in aranacak_sorgular:
                gorev_kuyrugu.put({"platform": platform, "kelime": sorgu["kelime"], "kategori": sorgu["kategori"]})
                
        WORKER_SAYISI = 2
        for i in range(WORKER_SAYISI):
            t = threading.Thread(target=platform_kaziyici_islem, args=(i+1, gorev_kuyrugu))
            t.daemon = True
            t.start()
        
        while not gorev_kuyrugu.empty():
            time.sleep(10)
        
        print("⏳ Kuyruk bitti. Yeni tur için 30 dakika dinleniliyor...")
        time.sleep(1800)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=bot_yoneticisi)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)