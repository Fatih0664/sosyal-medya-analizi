from playwright.sync_api import sync_playwright
import pandas as pd
import time

def mega_arama_kaziyici(sorgu):
    print(f"🚀 Mega Arama Operasyonu Başlıyor: '{sorgu}'")
    tum_sonuclar = []

    with sync_playwright() as p:
        # İnsan davranışı sergilemek için headless=False kullanıyoruz
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # ---------------------------------------------------------
        # 1. BING KAZIMA
        # ---------------------------------------------------------
        print("🔍 Bing.com taranıyor...")
        try:
            page.goto(f"https://www.bing.com/search?q={sorgu.replace(' ', '+')}")
            page.wait_for_timeout(2500) # İnsansı bekleme süresi
            
            # Bing sonuçları 'li.b_algo' sınıfında tutulur
            bing_elementleri = page.query_selector_all("li.b_algo")
            for b in bing_elementleri:
                baslik = b.query_selector("h2")
                link = b.query_selector("a")
                ozet = b.query_selector("div.b_caption p")
                
                if baslik and link:
                    tum_sonuclar.append({
                        'motor': 'Bing',
                        'baslik': baslik.inner_text(),
                        'ozet': ozet.inner_text() if ozet else "",
                        'link': link.get_attribute("href")
                    })
        except Exception as e:
            print(f"Bing taramasında hata: {e}")

        # ---------------------------------------------------------
        # 2. YAHOO KAZIMA
        # ---------------------------------------------------------
        print("🔍 Yahoo.com taranıyor...")
        try:
            page.goto(f"https://search.yahoo.com/search?p={sorgu.replace(' ', '+')}")
            page.wait_for_timeout(2500)
            
            # Yahoo sonuçları 'div.algo' sınıfında tutulur
            yahoo_elementleri = page.query_selector_all("div.algo")
            for y in yahoo_elementleri:
                baslik = y.query_selector("h3")
                link = y.query_selector("a")
                ozet = y.query_selector("div.compTitle ~ div") # Başlığın altındaki div
                
                if baslik and link:
                    tum_sonuclar.append({
                        'motor': 'Yahoo',
                        'baslik': baslik.inner_text(),
                        'ozet': ozet.inner_text() if ozet else "",
                        'link': link.get_attribute("href")
                    })
        except Exception as e:
            print(f"Yahoo taramasında hata: {e}")

        # ---------------------------------------------------------
        # 3. GOOGLE KAZIMA
        # ---------------------------------------------------------
        print("🔍 Google.com taranıyor...")
        try:
            page.goto(f"https://www.google.com/search?q={sorgu.replace(' ', '+')}")
            page.wait_for_timeout(3000)
            
            # Google sonuçları 'div.tF2Cxc' sınıfında tutulur
            google_elementleri = page.query_selector_all("div.tF2Cxc")
            for g in google_elementleri:
                baslik = g.query_selector("h3")
                link = g.query_selector("a")
                ozet = g.query_selector("div.VwiC3b")
                
                if baslik and link:
                    tum_sonuclar.append({
                        'motor': 'Google',
                        'baslik': baslik.inner_text(),
                        'ozet': ozet.inner_text() if ozet else "",
                        'link': link.get_attribute("href")
                    })
        except Exception as e:
            print(f"Google taramasında hata: {e}")

        browser.close()

    return tum_sonuclar

if __name__ == '__main__':
    hedef_sorgu = "yapay zeka trendleri 2026"
    veriler = mega_arama_kaziyici(hedef_sorgu)
    
    if veriler:
        df = pd.DataFrame(veriler)
        # Sütunları düzenleyelim
        df = df[['motor', 'baslik', 'ozet', 'link']]
        dosya_adi = "mega_arama_sonuclari.csv"
        df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
        
        print("\n--- ÇEKİLEN VERİNİN İLK 10 SATIRI ---")
        print(df.head(10))
        print(f"\n🎉 Zafer! Toplam {len(df)} sonuç '{dosya_adi}' dosyasına kaydedildi!")
    else:
        print("❌ Arama motorlarından veri çekilemedi.")