import yt_dlp
import pandas as pd
import json
import sqlite3

# Veritabanına bağlanıp verileri kaydeden fonksiyon
def veritabanina_kaydet(veriler_listesi):
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    
    eklenen_sayi = 0
    for veri in veriler_listesi:
        zengin_icerik = f"[{veri['tarih']}] {veri['metin']} (Etkileşim: {veri['etkilesim']})"
        
        cursor.execute("SELECT id FROM sosyal_medya_akis WHERE icerik = ?", (zengin_icerik,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO sosyal_medya_akis (platform, icerik)
                VALUES (?, ?)
            ''', (veri['platform'], zengin_icerik))
            eklenen_sayi += 1
            
    conn.commit()
    conn.close()
    return eklenen_sayi

def tiktok_kaziyici(hedef_url, hedef_video_sayisi=10):
    print(f"🚀 TikTok Veri Hattı başlatılıyor: {hedef_url}")
    
    # yt-dlp ayarları: Sadece meta-veriyi çek, videoyu indirme
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    
    veriler = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("TikTok sunucularından veriler sorgulanıyor...")
        try:
            result = ydl.extract_info(hedef_url, download=False)
            
            # Eğer bir kullanıcı profiliyse 'entries' listesi döner
            if 'entries' in result:
                videolar = list(result['entries'])[:hedef_video_sayisi]
                for video in videolar:
                    # Tarih verisini ayıklama ve formatlama
                    tarih_ham = video.get('upload_date')
                    tarih = f"{tarih_ham[:4]}-{tarih_ham[4:6]}-{tarih_ham[6:8]}" if tarih_ham else "Bilinmiyor"
                    
                    metin = video.get('title', '')
                    if not metin:
                        metin = "Video (Metin Yok)"
                    elif len(metin) > 120:
                        metin = metin[:120] + "..."
                        
                    etkilesim = video.get('like_count') or video.get('view_count') or 0
                    
                    veriler.append({
                        'tarih': tarih,
                        'platform': 'TikTok',
                        'metin': metin.replace('\n', ' '),
                        'etkilesim': etkilesim,
                        'url': video.get('url', '')
                    })
                    print(f"Veri yakalandı: {metin[:30]}...")
        except Exception as e:
            print(f"❌ Sorgu sırasında hata oluştu: {e}")

    print("\n--- PANDAS & VERİTABANI KAYDI ---")
    if veriler:
        # Veritabanına kaydetme işlemi
        eklenen_kayit = veritabanina_kaydet(veriler)
        
        df = pd.DataFrame(veriler)
        dosya_adi = "tiktok_verisi.csv"
        df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
        
        print(f"🎉 Zafer! Toplam {len(veriler)} adet TikTok verisi çekildi.")
        print(f"💾 {eklenen_kayit} yeni TikTok gönderisi veritabanına eklendi.")
    else:
        print("❌ Veri alınamadı. TikTok bağlantısı gizli veya yanlış olabilir.")

if __name__ == '__main__':
    url = "https://www.tiktok.com/@webtekno"
    tiktok_kaziyici(url, hedef_video_sayisi=10)