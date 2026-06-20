from playwright.sync_api import sync_playwright
import requests
from textblob import TextBlob

API_URL = "http://127.0.0.1:8000/api/v1/veri-gonder/"

def duygu_hesapla(metin):
    skor = TextBlob(str(metin)).sentiment.polarity
    if skor > 0.1: return "Pozitif 🟢", round(skor, 2)
    elif skor < -0.1: return "Negatif 🔴", round(skor, 2)
    return "Nötr ⚪", round(skor, 2)

def instagram_kaziyici(etiket):
    print(f"🕵️‍♂️ Insta Botu Uyandı: #{etiket} hedefleniyor...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="instagram_oturum.json")
        page = context.new_page()

        try:
            # networkidle: Sayfanın arka plandaki tüm yüklemeleri bitirmesini bekle
            page.goto(f"https://www.instagram.com/explore/tags/{etiket}/", wait_until="networkidle")
            print("⏳ Sayfa yüklendi, insan taklidi yapılarak aşağı kaydırılıyor...")
            
            # Tembel Yüklemeyi (Lazy Load) tetiklemek için fareyi 3 kez aşağı kaydır
            for _ in range(3):
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2500) # Her kaydırmadan sonra yeni verilerin inmesini bekle

            # Sayfadaki TÜM resimleri yakala (en garanti yöntem)
            gonderiler = page.locator("img").element_handles()
            
            basarili = 0
            for gonderi in gonderiler:
                icerik = gonderi.get_attribute("alt")
                
                # Boş içerikleri ve sadece 'profil resmi' yazanları ele, gerçek metni al
                if icerik and len(icerik) > 30 and "profile picture" not in icerik.lower() and "profil resmi" not in icerik.lower():
                    durum, skor = duygu_hesapla(icerik)
                    
                    paket = {
                        "platform": "Instagram",
                        "kategori": "Teknoloji",
                        "icerik": icerik,
                        "duygu_durumu": durum,
                        "duygu_skoru": skor
                    }
                    
                    res = requests.post(API_URL, json=paket)
                    if res.status_code == 201:
                        basarili += 1
                        print(f"✅ Insta'dan koparıldı: {icerik[:50]}...")
                        
            print(f"\n🎉 Instagram görevi tamamlandı. API'ye {basarili} yeni veri aktarıldı.")

        except Exception as e:
            print(f"Hata oluştu: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    instagram_kaziyici("yapayzeka")
