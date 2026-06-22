import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd
import sqlite3

def veritabanina_kaydet(veriler_listesi):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    eklenen_sayi = 0
    for veri in veriler_listesi:
        zengin_icerik = f"[{veri['tarih']}] {veri['metin']} (Beğeni: {veri['etkilesim']})"
        cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO sosyal_medya_akis (platform, icerik) VALUES (?, ?)', (veri['platform'], zengin_icerik))
            eklenen_sayi += 1
    conn.commit()
    conn.close()
    return eklenen_sayi

def instagram_selenium_kaziyici(hedef_hesap="webtekno", hedef_sayi=5):
    print("🚀 Instagram Nihai Kazıcı (Selenium) başlatılıyor...")
    options = uc.ChromeOptions()
    options.add_argument("--lang=tr-TR")
    
    # Twitter'da yarattığımız ve çalıştığını kanıtladığımız profili kullanıyoruz
    profil_yolu = os.path.join(os.getcwd(), "chrome_profil")
    options.add_argument(f"--user-data-dir={profil_yolu}")
    
    driver = uc.Chrome(options=options, version_main=149)
    
    try:
        url = f"https://www.instagram.com/{hedef_hesap}/"
        print(f"{url} adresine gidiliyor...")
        driver.get(url)
        
        # DİKKAT: Tarayıcı açıldığında Instagram giriş yapmanı isterse,
        # bu 8 saniye içinde hızlıca elinle giriş yap. Tarayıcı bunu kaydedecek!
        print("Sayfanın yüklenmesi (ve gerekiyorsa giriş yapman) için 8 saniye bekleniyor...")
        time.sleep(8)
        
        # --- 1. AŞAMA: PROFİLDEKİ GÖNDERİ LİNKLERİNİ TOPLAMA ---
        print("Gönderi linkleri toplanıyor...")
        linkler = set()
        durma_sayaci = 0
        
        while len(linkler) < hedef_sayi and durma_sayaci < 4:
            # Instagram postları /p/ veya /reel/ içerir
            a_taglari = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
            baslangic = len(linkler)
            
            for a in a_taglari:
                href = a.get_attribute('href')
                if href:
                    linkler.add(href)
                    if len(linkler) >= hedef_sayi:
                        break
                        
            if len(linkler) == baslangic:
                durma_sayaci += 1
            else:
                durma_sayaci = 0
                
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
        linkler = list(linkler)[:hedef_sayi]
        print(f"✅ Toplam {len(linkler)} gönderi bulundu. İçeriklerine giriliyor...")
        
        # --- 2. AŞAMA: LİNKLERİN İÇİNE GİRİP TEMİZ VERİ ÇEKME ---
        veriler = []
        for i, link in enumerate(linkler):
            try:
                driver.get(link)
                time.sleep(3.5) 
                
                # Tarih
                try:
                    tarih_el = driver.find_element(By.TAG_NAME, "time")
                    tarih = tarih_el.get_attribute("datetime")[:10] 
                except:
                    tarih = "Bilinmiyor"
                    
                # Beğeni ve Metin (Instagram bunları <meta> etiketine gizler, biz de oradan çalarız)
                try:
                    meta_desc = driver.find_element(By.CSS_SELECTOR, "meta[property='og:description']").get_attribute("content")
                    # Örnek içerik: "15K likes, 234 comments - webtekno on June 22..."
                    bolumler = meta_desc.split(' - ', 1)
                    etkilesim = bolumler[0].split(',')[0].strip() 
                    
                    if len(bolumler) > 1 and ":" in bolumler[1]:
                        metin = bolumler[1].split(':', 1)[1].strip()
                    else:
                        metin = "Görsel/Video (Metin Yok)"
                except:
                    etkilesim = "0"
                    metin = "Veri alınamadı"
                    
                if len(metin) > 120:
                    metin = metin[:120] + "..."
                    
                if metin != "Veri alınamadı":
                    veriler.append({
                        'tarih': tarih,
                        'platform': 'Instagram',
                        'metin': metin.replace('\n', ' '),
                        'etkilesim': etkilesim
                    })
                    print(f"[{i+1}/{len(linkler)}] Gönderi başarıyla yakalandı.")
                    
            except Exception as e:
                print(f"❌ Hata: {e}")
                continue
                
        # --- 3. AŞAMA: VERİTABANINA KAYIT ---
        print("\n--- PANDAS & VERİTABANI KAYDI ---")
        if veriler:
            eklenen_kayit = veritabanina_kaydet(veriler)
            
            df = pd.DataFrame(veriler)
            df.to_csv(f"instagram_{hedef_hesap}_selenium.csv", index=False, encoding='utf-8-sig')
            
            print(f"🎉 Zafer! Toplam {len(veriler)} gönderi çekildi.")
            print(f"💾 {eklenen_kayit} yeni Instagram gönderisi veritabanına eklendi.")
        else:
            print("❌ Hiç gönderi toplanamadı.")
            
    except Exception as e:
        print(f"Kritik Hata: {e}")
    finally:
        driver.quit()
        print("Tarayıcı kapatıldı.")

if __name__ == '__main__':
    # Hızlı test için hedefi 5 yaptık. Başarılı olursa burayı 50 yapabilirsin.
    instagram_selenium_kaziyici(hedef_hesap="webtekno", hedef_sayi=50)