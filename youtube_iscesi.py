from playwright.sync_api import sync_playwright
import requests
import time
from textblob import TextBlob

API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

def duygu_hesapla(metin):
    # İstatistikçi kimliğin için duygu analizi motoru
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def youtube_kaziyici(anahtar_kelime):
    print(f"📺 YouTube Botu Göreve Başladı: '{anahtar_kelime}' aranıyor...")
    with sync_playwright() as p:
        # YouTube botları kolay yakalar, bu yüzden 'stealth' benzeri ayarlar yapıyoruz
        browser = p.chromium.launch(headless=False) # İzlemek istersen True yapabilirsin
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # YouTube arama sonuçları sayfasına git
            search_url = f"https://www.youtube.com/results?search_query={anahtar_kelime}"
            page.goto(search_url, wait_until="networkidle")
            
            # YouTube "Tembel Yükleme" (Lazy Load) yaptığı için sayfayı biraz aşağı kaydırıyoruz
            print("⏳ YouTube sonuçları taranıyor...")
            for _ in range(2):
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)

            # Video başlıklarını içeren etiketleri yakala (ytd-video-renderer içindeki #video-title)
            videolar = page.query_selector_all("a#video-title")
            
            basarili = 0
            for v in videolar[:20]: # İlk 20 video sonucunu al
                baslik = v.get_attribute("title")
                if baslik and len(baslik) > 10:
                    durum, skor = duygu_hesapla(baslik)
                    
                    paket = {
                        "platform": "YouTube",
                        "kategori": "Akademik/Teknoloji", # Vizyonuna göre kategori dinamik olabilir
                        "icerik": baslik,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor
                    }
                    
                    # Veriyi merkeze (FastAPI) ateşle
                    res = requests.post(API_URL, json=paket)
                    if res.status_code == 201:
                        basarili += 1
                        print(f"✅ YT'den çekildi: {baslik[:50]}...")
            
            print(f"\n🎉 YouTube görevi tamamlandı. API'ye {basarili} yeni veri aktarıldı.")

        except Exception as e:
            print(f"YouTube Botu bir engelle karşılaştı: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Senin büyük vizyonun için önemli anahtar kelimeler
    youtube_kaziyici("yapay zeka gelecek araştırmaları")
