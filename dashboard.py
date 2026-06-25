import streamlit as st
import pandas as pd
from supabase import create_client
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dijital İstihbarat Panosu", page_icon="🌍", layout="wide")

st.title("🌍 Dijital İstihbarat ve Sosyal Medya Analiz Panosu")
st.markdown("Arka planda çalışan botun topladığı verileri filtreleyip analiz edin.")

# --- SUPABASE BAĞLANTISI ---
SUPABASE_URL = "https://oskhluimvjvjhbtjqnoo.supabase.co"
SUPABASE_KEY = "sb_secret_MsMqFI2v9VF68mf6MyKhTg_wLLrlTky"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase bağlantı hatası: {e}")
        return None

supabase = init_connection()

@st.cache_data(ttl=60)
def veri_getir():
    if supabase is None:
        return pd.DataFrame()
        
    try:
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(500).execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
        return df
    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        return pd.DataFrame()

# Veriyi Çek
st.write("Veriler Supabase bulutundan çekiliyor... ⏳")
df = veri_getir()

if not df.empty:
    # --- YAN MENÜ (FİLTRELEME) ---
    st.sidebar.header("🔍 Filtreleme")
    
    secilen_platformlar = st.sidebar.multiselect(
        "Platform Seçin:",
        options=df['platform'].unique(),
        default=df['platform'].unique()
    )
    
    secilen_kategoriler = st.sidebar.multiselect(
        "Kategori Seçin:",
        options=df['kategori'].unique(),
        default=df['kategori'].unique()
    )
    
    # Veriyi filtrelere göre daralt
    filtrelenmis_df = df[
        (df['platform'].isin(secilen_platformlar)) & 
        (df['kategori'].isin(secilen_kategoriler))
    ]
    
    if filtrelenmis_df.empty:
        st.warning("Seçilen filtrelere uygun veri bulunamadı. Lütfen filtreleri genişletin.")
    else:
        # --- 1. ÜST KISIM: Özet Metrikler ---
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        toplam_veri = len(filtrelenmis_df)
        pozitif_veri = len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Pozitif', na=False)])
        negatif_veri = len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Negatif', na=False)])
        notr_veri = len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Nötr', na=False)])
        
        col1.metric("📌 Toplam Çekilen Veri", toplam_veri)
        col2.metric("🟢 Pozitif İçerik", pozitif_veri)
        col3.metric("🔴 Negatif İçerik", negatif_veri)
        col4.metric("⚪ Nötr İçerik", notr_veri)
        
        st.markdown("---")
        
        # --- 2. ORTA KISIM: Grafikler ---
        grafik_kolon1, grafik_kolon2 = st.columns(2)
        
        with grafik_kolon1:
            st.subheader("📊 Platform Dağılımı")
            platform_sayilari = filtrelenmis_df['platform'].value_counts()
            st.bar_chart(platform_sayilari)
            
        with grafik_kolon2:
            st.subheader("🎯 Duygu Dağılımı (Pasta Grafik)")
            duygu_sayilari = filtrelenmis_df['duygu_durumu'].value_counts()
            
            # Matplotlib ile Pasta Grafik
            fig, ax = plt.subplots(figsize=(5, 5))
            
            # Renkleri otomatik ayarlama
            renkler = []
            for etiket in duygu_sayilari.index:
                if 'Pozitif' in etiket: renkler.append('#2ecc71')
                elif 'Negatif' in etiket: renkler.append('#e74c3c')
                else: renkler.append('#bdc3c7')
                
            ax.pie(duygu_sayilari, labels=duygu_sayilari.index, autopct='%1.1f%%', startangle=90, colors=renkler)
            ax.axis('equal') 
            st.pyplot(fig)
            
        st.markdown("---")
        
        # --- 3. KELİME BULUTU ---
        st.subheader("☁️ En Çok Geçen Kelimeler")
        tum_metin = " ".join(filtrelenmis_df['icerik'].dropna().astype(str).tolist())
        
        if len(tum_metin) > 20:
            # WordCloud oluştur
            wordcloud = WordCloud(width=800, height=300, background_color="white", max_words=100, colormap="viridis").generate(tum_metin)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        else:
            st.info("Kelime bulutu oluşturmak için henüz yeterli uzunlukta metin yok.")

        st.markdown("---")
        
        # --- 4. ALT KISIM: Tablo ve İndirme Butonu ---
        st.subheader("🔍 Filtrelenmiş Canlı Veriler")
        gosterilecek_tablo = filtrelenmis_df[['created_at', 'platform', 'kategori', 'duygu_durumu', 'duygu_skoru', 'icerik']]
        st.dataframe(gosterilecek_tablo, use_container_width=True, height=400)
        
        # Excel (CSV) İndirme Butonu
        st.markdown("<br>", unsafe_allow_html=True)
        csv_veri = filtrelenmis_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Bu Tabloyu Excel (CSV) Olarak İndir",
            data=csv_veri,
            file_name=f'analiz_raporu_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )

else:
    st.warning("Veritabanında gösterilecek taze veri yok. Botun veri toplamasını bekleyin.")