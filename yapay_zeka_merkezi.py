import pandas as pd
from groq import Groq

# DİKKAT: Groq API anahtarını buraya yapıştır
API_KEY = "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"
client = Groq(api_key=API_KEY)

def yapay_zeka_ozeti_cikar(excel_yolu="Gunluk_Istihbarat_Raporu.xlsx"):
    print("🧠 Llama-3 (Groq) verileri inceliyor, rapor hazırlanıyor...")
    
    try:
        # Excel'den sadece son 3 günün trendini okuyoruz
        df_frekans = pd.read_excel(excel_yolu, sheet_name='Günlük Frekans').tail(3)
        df_duygu = pd.read_excel(excel_yolu, sheet_name='Ortalama Duygu Skoru').tail(3)

        veri_metni = f"--- SON 3 GÜNÜN PLATFORM MESAJ FREKANSLARI ---\n{df_frekans.to_string()}\n\n"
        veri_metni += f"--- SON 3 GÜNÜN ORTALAMA DUYGU SKORLARI (-1 Negatif, 1 Pozitif) ---\n{df_duygu.to_string()}"

        prompt = f"""
        Sen kıdemli bir dijital istihbarat analistisin. 
        Aşağıda, çeşitli sosyal medya platformlarından çekilmiş son 3 günlük mesaj frekansları ve NLP (Doğal Dil İşleme) duygu skorları yer almaktadır.
        
        VERİLER:
        {veri_metni}
        
        GÖREVİN:
        Bu verileri dikkatlice analiz ederek yöneticiler için 3-4 paragraflık, son derece profesyonel, akıcı ve stratejik bir "Günlük Dijital İstihbarat Özeti" yazman. Raporu tamamen Türkçe yaz.
        
        LÜTFEN ŞUNLARA DİKKAT ET:
        1. Hangi platformda anormal bir mesaj artışı/azalışı var?
        2. Platformların duygu durumları ne yönde değişiyor?
        3. Sayılara boğulmadan, doğrudan çıkarımları (insight) ve genel atmosferi aktar.
        """

        # Groq üzerinden en güncel Llama modeline API çağrısı
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen uzman bir veri analisti ve istihbarat uzmanısın. Her zaman Türkçe yanıt verirsin."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile", # <-- BURAYI GÜNCELLEDİK
            temperature=0.5,
            max_tokens=1024
        )
        
        ozet_metni = response.choices[0].message.content

        print("\n" + "="*60)
        print("📋 GÜNLÜK DİJİTAL İSTİHBARAT ÖZETİ (LLAMA-3)")
        print("="*60)
        print(ozet_metni)
        print("="*60 + "\n")
        
        return ozet_metni

    except FileNotFoundError:
        print("❌ Hata: 'Gunluk_Istihbarat_Raporu.xlsx' dosyası bulunamadı. Önce 'python analiz_motoru.py' komutunu çalıştırdığından emin ol.")
        return None
    except Exception as e:
        print(f"❌ Yapay zeka analizi sırasında beklenmeyen bir hata oluştu: {e}")
        return None

if __name__ == "__main__":
    yapay_zeka_ozeti_cikar()
