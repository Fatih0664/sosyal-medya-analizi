from duckduckgo_search import DDGS
import pandas as pd

def coklu_arama(sorgu, limit=10):
    print(f"🌐 İnternetin tüm köşeleri taranıyor: '{sorgu}'...")
    veriler = []
    
    with DDGS() as ddgs:
        # Hem Google hem de DuckDuckGo algoritmalarına hitap eden meta-arama
        results = ddgs.text(sorgu, max_results=limit)
        
        for r in results:
            veriler.append({
                'platform': 'Genel Arama (DuckDuckGo/Bing)',
                'baslik': r['title'],
                'ozet': r['body'],
                'link': r['href']
            })
            
    return pd.DataFrame(veriler)

if __name__ == '__main__':
    df = coklu_arama("yapay zeka trendleri 2026")
    df.to_csv("master_arama_sonuclari.csv", index=False, encoding='utf-8-sig')
    print(f"🎉 Toplam {len(df)} sonuç 'master_arama_sonuclari.csv' dosyasına kaydedildi.")