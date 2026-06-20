import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd
from datetime import datetime

def tam_kapsamli_instagram_kaziyici(hedef_hesap="webtekno", hedef_link_sayisi=50):
    print("🚀 Tam Kapsamlı Kazıyıcı (Scroll + Veri Çekme) başlatılıyor...")
    options = uc.ChromeOptions()
    
    # Altın anahtarımız (çerezler)
    profil_yolu = os.path.join(os.getcwd(), "chrome_profil")
    options.add_argument(f"--user-data-dir={profil_yolu}")
    
    driver = uc.Chrome(options=options, version_main=149)
    
    try:
        print(f"{hedef_hesap} profiline gidiliyor...")
        driver.get(f"https://www.instagram.com/{hedef_hesap}/")
        time.sleep(5)
        
        print("--- 1. AŞAMA: LİNKLERİ TOPLAMA ---")
        gonderi_linkleri = set()
        eski_uzunluk = 0
        deneme_sayaci = 0
        
        # Sayfa kaydırma döngüsü
        while len(gonderi_linkleri) < hedef_link_sayisi:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Yeni postların DOM'a yüklenmesi için esnek bekleme
            
            elementler = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            for el in elementler:
                href = el.get_attribute('href')
                if href:
                    gonderi_linkleri.add(href)
            
            print(f"Toplanan link: {len(gonderi_linkleri)} / {hedef_link_sayisi}")
            
            # Sistem takılırsa (sayfa sonu vs.) sonsuz döngüye girmemesi için
            if len(gonderi_linkleri) == eski_uzunluk:
                deneme_sayaci += 1
                if deneme_sayaci > 3:
                    print("Daha fazla kaydırılamıyor, sayfa sonuna gelinmiş olabilir.")
                    break
            else:
                eski_uzunluk = len(gonderi_linkleri)
                deneme_sayaci = 0
                
        link_listesi = list(gonderi_linkleri)[:hedef_link_sayisi]
        print(f"\n--- 2. AŞAMA: VERİ ÇIKARIMI ({len(link_listesi)} GÖNDERİ) ---")
        
        veriler = []
        # Her bir linke tek tek gidip içeriği çekiyoruz
        for i, link in enumerate(link_listesi, 1):
            print(f"[{i}/{len(link_listesi)}] İşleniyor: {link.split('instagram.com/')[1]}")
            driver.get(link)
            
            # Instagram'ın botumuzu banlamaması için her sayfa arasında mutlaka dinlenmeliyiz
            time.sleep(4) 
            
            post_tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            post_metin = ""
            post_etkilesim = "0"
            
            # 1. Tarih Çekme
            try:
                zaman_elementi = driver.find_element(By.TAG_NAME, "time")
                ham_tarih = zaman_elementi.get_attribute("datetime")
                if ham_tarih:
                    post_tarih = ham_tarih.split("T")[0] + " " + ham_tarih.split("T")[1][:8]
            except: pass
                
            # 2. Metin Çekme (Genellikle h1 içindedir)
            try:
                metin_elementi = driver.find_element(By.CSS_SELECTOR, "h1[dir='auto']")
                post_metin = metin_elementi.text
            except: pass
            
            # 3. Beğeni Çekme
            try:
                # "beğenme" veya "likes" kelimesi geçen elementleri yakalar
                begeni_elementi = driver.find_element(By.XPATH, "//span[contains(text(), 'beğenme') or contains(text(), 'likes')] | //a[contains(text(), 'beğenme') or contains(text(), 'likes')]")
                post_etkilesim = begeni_elementi.text.split()[0]
            except: pass
                
            veriler.append({
                'tarih': post_tarih,
                'platform': 'Instagram',
                'metin': post_metin.replace('\n', ' ')[:80] + "...", # Terminalde düzgün görünmesi için temizliyoruz
                'etkilesim': post_etkilesim
            })
            
        print("\n--- 3. AŞAMA: PANDAS İLE KAYIT ---")
        if veriler:
            df = pd.DataFrame(veriler)
            dosya_adi = f"instagram_{hedef_hesap}_verisi.csv"
            
            # Türkçe karakterlerin bozulmaması için utf-8-sig
            df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
            
            print("\n--- ÇEKİLEN VERİNİN İLK 5 SATIRI ---")
            print(df.head())
            print(f"\n🎉 Veriler başarıyla '{dosya_adi}' dosyasına kaydedildi!")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")
    finally:
        driver.quit()
        print("Tarayıcı kapatıldı.")

if __name__ == '__main__':
    tam_kapsamli_instagram_kaziyici()