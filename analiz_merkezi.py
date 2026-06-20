import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Sosyal Medya & Web Analiz Merkezi", layout="wide")

# Sol Menü (Sidebar) Kontrolleri
st.sidebar.title("Kontrol Paneli")
if st.sidebar.button("🔄 Verileri Yenile"):
    st.rerun()
st.sidebar.success("Sistem tam kapasite çalışıyor.")

st.title("📊 Mega Analiz Merkezi ve Duygu Motoru")

# --- ANALİTİK MOTOR FONKSİYONLARI ---
def duygu_analizi(metin):
    analiz = TextBlob(str(metin))
    if analiz.sentiment.polarity > 0.1:
        return 'Pozitif 🟢'
    elif analiz.sentiment.polarity < -0.1:
        return 'Negatif 🔴'
    else:
        return 'Nötr ⚪'

def link_temizle(link):
    link = str(link)
    if "bing.com/ck/a" in link or "/images/search" in link:
        return "Yönlendirme/Görsel Linki (Temizlendi)"
    return link

# --- BÖLÜM 1: MULTI-SEARCH VE YAPAY ZEKA DUYGU ANALİZİ ---
st.markdown("### 🌐 Web Arama Sonuçları ve Duygu Analizi")
try:
    df_mega = pd.read_csv("mega_arama_sonuclari.csv")
    df_mega['link'] = df_mega['link'].apply(link_temizle)
    df_mega['Duygu Durumu'] = df_mega['baslik'].apply(duygu_analizi)
    
    # Güncellenmiş genişlik parametresi (width='stretch')
    st.dataframe(df_mega[['motor', 'baslik', 'Duygu Durumu', 'link']], width='stretch')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_motor = px.pie(df_mega, names='motor', title="Veri Kaynakları Dağılımı", hole=0.4)
        st.plotly_chart(fig_motor, width='stretch')
        
    with col2:
        duygu_sayilari = df_mega['Duygu Durumu'].value_counts().reset_index()
        duygu_sayilari.columns = ['Duygu', 'Sayı']
        fig_duygu = px.bar(duygu_sayilari, x='Duygu', y='Sayı', title="Arama Sonuçları Duygu Analizi", color='Duygu')
        st.plotly_chart(fig_duygu, width='stretch')
        
    with col3:
        st.markdown("**☁️ Kelime Bulutu (Sık Tekrar Eden Kavramlar)**")
        # float/NaN hatasını engellemek için boş satırları uçurup listeye çeviriyoruz
        temiz_basliklar = df_mega['baslik'].dropna().astype(str).tolist()
        tum_metinler = " ".join(temiz_basliklar)
        
        if tum_metinler.strip():
            wordcloud = WordCloud(width=800, height=800, background_color='white', min_font_size=10).generate(tum_metinler)
            fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
            ax.imshow(wordcloud)
            ax.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig)
        else:
            st.info("Kelime bulutu oluşturulacak metin bulunamadı.")

except FileNotFoundError:
    st.warning("⚠️ 'mega_arama_sonuclari.csv' dosyası bulunamadı. Lütfen önce arama_kaziyici.py scriptini çalıştırın.")

# --- BÖLÜM 2: WHATSAPP GERÇEK ZAMANLI VERİ AKIŞI ---
st.markdown("---")
st.markdown("### 🟢 Canlı WhatsApp Akışı")

wp_dosya = "whatsapp_mesajlar.csv"
if os.path.exists(wp_dosya):
    try:
        df_wp = pd.read_csv(wp_dosya, header=None, names=["Tarih/Kim", "Mesaj"], encoding="utf-8-sig")
        # En taze 10 mesajı en üstte gösterecek şekilde sıralı basıyoruz
        st.dataframe(df_wp.tail(10), width='stretch', hide_index=True)
    except Exception as e:
        st.error(f"WhatsApp verisi okunurken bir sorun oluştu: {e}")
else:
    st.info("📩 Henüz canlı veri akışı loglanmadı. Arka planda 'whatsapp_dinleyici.py' çalışmaya başladığında mesajlar buraya düşecektir.")