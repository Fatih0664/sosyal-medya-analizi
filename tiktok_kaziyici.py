import yt_dlp
import pandas as pd
import json

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
        result = ydl.extract_info(hedef_url, download=False)
        
        # Eğer bir kullanıcı profiliyse 'entries' listesi döner
        if 'entries' in result:
            videolar = result['entries'][:hedef_video_sayisi]
            for video in videolar:
                # TikTok'un bize gönderdiği JSON içinden verileri ayıklıyoruz
                veriler.append({
                    'tarih': 'Mobil Veri',
                    'platform': 'TikTok',
                    'metin': video.get('title', '')[:80] + "...",
                    'etkilesim': video.get('like_count', 0),
                    'url': video.get('url', '')
                })
                print(f"Veri yakalandı: {video.get('title')[:30]}...")

    if veriler:
        df = pd.DataFrame(veriler)
        dosya_adi = "tiktok_verisi.csv"
        df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
        print(f"\n🎉 Zafer! {len(veriler)} adet TikTok verisi '{dosya_adi}' dosyasına kaydedildi!")
    else:
        print("❌ Veri alınamadı. TikTok bağlantısı gizli veya yanlış olabilir.")

if __name__ == '__main__':
    # Örnek: Bir kullanıcı profilinin URL'si
    url = "https://www.tiktok.com/@webtekno"
    tiktok_kaziyici(url)