from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
import sqlite3
import os
import csv

def veritabanina_kaydet(kim_tarih, mesaj):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    zengin_icerik = f"[{kim_tarih}] {mesaj}"
    cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO sosyal_medya_akis (platform, icerik, duygu_skoru, duygu_durumu)
            VALUES (?, ?, ?, ?)
        ''', ('WhatsApp', zengin_icerik, 0.0, 'Nötr ⚪'))
        conn.commit()
    conn.close()

def whatsapp_dinleyici():
    print("🚀 WhatsApp Evrensel Dinleyici (Kanal + Sohbet) başlatılıyor...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("🟢 WhatsApp Web takip ediliyor. Yeni mesajlar veya Kanal duyuruları bekleniyor...")
    except Exception as e:
        print("\n❌ BAĞLANTI HATASI: Chrome Hata Ayıklama modunda bulunamadı!")
        return

    with open("whatsapp_mesajlar.csv", "w", encoding="utf-8-sig", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Tarih/Kim", "Mesaj"])

    dinlenen_mesajlar = set()
    
    try:
        while True:
            # Sadece kişisel mesajları değil, 'data-id'ye sahip TÜM mesaj baloncuklarını yakala
            mesaj_elementleri = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
            
            for mesaj in mesaj_elementleri:
                try:
                    mesaj_id = mesaj.get_attribute("data-id")
                    
                    if mesaj_id not in dinlenen_mesajlar:
                        metin_tamami = mesaj.text
                        if not metin_tamami or len(metin_tamami) < 2:
                            continue 
                            
                        # 1. SENARYO: Bu normal bir kişisel/grup sohbeti mi?
                        kimlik_kutusu = mesaj.find_elements(By.CSS_SELECTOR, "div[data-pre-plain-text]")
                        
                        if kimlik_kutusu:
                            veri_etiketi = kimlik_kutusu[0].get_attribute("data-pre-plain-text")
                            temiz_metin = kimlik_kutusu[0].text
                        else:
                            # 2. SENARYO: Bu bir WhatsApp Kanalı! 
                            veri_etiketi = "[Kanal Yayını]"
                            temiz_metin = metin_tamami
                        
                        print(f"\n📩 YAKALANDI {veri_etiketi}: {temiz_metin[:40]}...")
                        
                        # CSV'ye güvenli yazım
                        with open("whatsapp_mesajlar.csv", "a", encoding="utf-8-sig", newline='') as f:
                            writer = csv.writer(f)
                            temiz_veri_etiketi = veri_etiketi.replace('[', '').replace(']', '').replace(',', ' -').strip()
                            temiz_icerik = temiz_metin.replace('\n', ' ').strip()
                            writer.writerow([temiz_veri_etiketi, temiz_icerik])
                        
                        veritabanina_kaydet(veri_etiketi, temiz_metin.replace('\n', ' '))
                        dinlenen_mesajlar.add(mesaj_id)
                        
                except StaleElementReferenceException:
                    # KORUMA KALKANI: Eğer mesaj biz okurken güncellendiyse (bayatladıysa), 
                    # çökmek yerine es geç. Döngü bir sonraki turda zaten güncel halini yakalayacak.
                    continue
            
            time.sleep(2.5) 
            
    except KeyboardInterrupt:
        print("\n🛑 Dinleme durduruldu.")

if __name__ == '__main__':
    whatsapp_dinleyici()