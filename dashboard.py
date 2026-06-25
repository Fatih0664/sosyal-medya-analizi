import streamlit as st
import pandas as pd
from supabase import create_client
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
import io

# --- ÇOKLU DİL SÖZLÜĞÜ ---
DIL_SECENEKLERI = {
    "Türkçe": {
        "title": "Web ve Sosyal Medya Analizi",
        "lang_select": "🌐 Dil Seçimi / Language",
        "plat_select": "🌍 Tüm Platformlar",
        "cat_select": "📂 Konu Seçin",
        "country_select": "🗺️ Tüm Dünya (Ülke Seçin)",
        "total": "📌 Toplam Çekilen Veri",
        "pos": "🟢 Pozitif İçerik",
        "neg": "🔴 Negatif İçerik",
        "neu": "⚪ Nötr İçerik",
        "chart_plat": "📊 Platform Dağılımı",
        "chart_emo": "🎯 Duygu Dağılımı",
        "wordcloud": "☁️ En Çok Geçen Kelimeler",
        "table": "🔍 Filtrelenmiş Canlı Veriler",
        "download": "📥 Bu Tabloyu Excel Olarak İndir",
        "no_filter": "Seçilen filtrelere uygun veri bulunamadı.",
        "no_data": "Veritabanında henüz veri yok."
    },
    "English": {
        "title": "Web and Social Media Analysis",
        "lang_select": "🌐 Language",
        "plat_select": "🌍 All Platforms",
        "cat_select": "📂 Select Topic",
        "country_select": "🗺️ Whole World (Select Country)",
        "total": "📌 Total Data",
        "pos": "🟢 Positive Content",
        "neg": "🔴 Negative Content",
        "neu": "⚪ Neutral Content",
        "chart_plat": "📊 Platform Distribution",
        "chart_emo": "🎯 Sentiment Distribution",
        "wordcloud": "☁️ Most Frequent Words",
        "table": "🔍 Filtered Live Data",
        "download": "📥 Download as Excel",
        "no_filter": "No data found for the selected filters.",
        "no_data": "No data in the database yet."
    },
    "Deutsch": {
        "title": "Web- und Social-Media-Analyse",
        "lang_select": "🌐 Sprache",
        "plat_select": "🌍 Alle Plattformen",
        "cat_select": "📂 Thema wählen",
        "country_select": "🗺️ Ganze Welt (Land wählen)",
        "total": "📌 Gesamtdaten",
        "pos": "🟢 Positiver Inhalt",
        "neg": "🔴 Negativer Inhalt",
        "neu": "⚪ Neutraler Inhalt",
        "chart_plat": "📊 Plattformverteilung",
        "chart_emo": "🎯 Stimmungsverteilung",
        "wordcloud": "☁️ Häufigste Wörter",
        "table": "🔍 Gefilterte Live-Daten",
        "download": "📥 Als Excel herunterladen",
        "no_filter": "Keine Daten für diese Filter gefunden.",
        "no_data": "Noch keine Daten in der Datenbank."
    },
    "Français": {
        "title": "Analyse du Web et des Réseaux Sociaux",
        "lang_select": "🌐 Langue",
        "plat_select": "🌍 Toutes les plateformes",
        "cat_select": "📂 Choisir le sujet",
        "country_select": "🗺️ Monde entier (Choisir le pays)",
        "total": "📌 Données Totales",
        "pos": "🟢 Contenu Positif",
        "neg": "🔴 Contenu Négatif",
        "neu": "⚪ Contenu Neutre",
        "chart_plat": "📊 Distribution",
        "chart_emo": "🎯 Sentiments",
        "wordcloud": "☁️ Mots les plus fréquents",
        "table": "🔍 Données filtrées",
        "download": "📥 Télécharger en Excel",
        "no_filter": "Aucune donnée trouvée.",
        "no_data": "Aucune donnée dans la base."
    },
    "中文": {
        "title": "网络和社交媒体分析",
        "lang_select": "🌐 语言",
        "plat_select": "🌍 所有平台",
        "cat_select": "📂 选择主题",
        "country_select": "🗺️ 全世界 (选择国家)",
        "total": "📌 总数据",
        "pos": "🟢 正面内容",
        "neg": "🔴 负面内容",
        "neu": "⚪ 中立内容",
        "chart_plat": "📊 平台分布",
        "chart_emo": "🎯 情绪分布",
        "wordcloud": "☁️ 常用词",
        "table": "🔍 过滤后的数据",
        "download": "📥 下载为 Excel",
        "no_filter": "未找到数据。",
        "no_data": "尚无数据。"
    },
    "العربية": {
        "title": "تحليل الويب ووسائل التواصل الاجتماعي",
        "lang_select": "🌐 اللغة",
        "plat_select": "🌍 جميع المنصات",
        "cat_select": "📂 اختر الموضوع",
        "country_select": "🗺️ جميع أنحاء العالم (اختر الدولة)",
        "total": "📌 إجمالي البيانات",
        "pos": "🟢 محتوى إيجابي",
        "neg": "🔴 محتوى سلبي",
        "neu": "⚪ محتوى محايد",
        "chart_plat": "📊 توزيع المنصات",
        "chart_emo": "🎯 توزيع المشاعر",
        "wordcloud": "☁️ الكلمات الشائعة",
        "table": "🔍 البيانات المفلترة",
        "download": "📥 تحميل Excel",
        "no_filter": "لم يتم العثور على بيانات.",
        "no_data": "لا توجد بيانات."
    }
}

# Sabit Listeler
TUM_PLATFORMLAR = ["Google", "Bing", "Yahoo", "Facebook", "YouTube", "X (Twitter)", "Telegram", "Instagram", "TikTok", "WhatsApp"]
ULKELER = ["Türkiye", "ABD", "Almanya", "İngiltere", "Fransa", "Rusya", "Çin", "Japonya", "Güney Kore", "İtalya", "Brezilya", "Hindistan", "Mısır", "Suudi Arabistan"]

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Web ve Sosyal Medya Analizi", page_icon="🌍", layout="wide")

# YAN MENÜ: Dil Seçimi
secilen_dil = st.sidebar.selectbox("🌐 Dil Seçimi / Language", options=list(DIL_SECENEKLERI.keys()))
lang = DIL_SECENEKLERI[secilen_dil]

st.title(lang["title"])

# --- SUPABASE BAĞLANTISI ---
SUPABASE_URL = "https://oskhluimvjvjhbtjqnoo.supabase.co"
SUPABASE_KEY = "sb_secret_MsMqFI2v9VF68mf6MyKhTg_wLLrlTky"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

@st.cache_data(ttl=60)
def veri_getir():
    if supabase is None: return pd.DataFrame()
    try:
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(500).execute()
        df = pd.DataFrame(response.data)
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Veritabanında ülke sütunu olmadığı için şimdilik görsel amaçlı varsayılan ülke ekliyoruz
            if 'ulke' not in df.columns:
                df['ulke'] = "Türkiye"
                
        return df
    except:
        return pd.DataFrame()

df = veri_getir()

if not df.empty:
    # --- YAN MENÜ (FİLTRELEME) ---
    st.sidebar.markdown("---")
    
    secilen_ulkeler = st.sidebar.multiselect(
        lang["country_select"],
        options=ULKELER,
        default=["Türkiye"]
    )

    secilen_platformlar = st.sidebar.multiselect(
        lang["plat_select"],
        options=TUM_PLATFORMLAR,
        default=TUM_PLATFORMLAR
    )
    
    secilen_kategoriler = st.sidebar.multiselect(
        lang["cat_select"],
        options=df['kategori'].unique(),
        default=df['kategori'].unique()
    )
    
    filtrelenmis_df = df[
        (df['platform'].isin(secilen_platformlar)) & 
        (df['kategori'].isin(secilen_kategoriler)) &
        (df['ulke'].isin(secilen_ulkeler))
    ]
    
    if filtrelenmis_df.empty:
        st.warning(lang["no_filter"])
    else:
        # --- Özet Metrikler ---
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(lang["total"], len(filtrelenmis_df))
        col2.metric(lang["pos"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Pozitif', na=False)]))
        col3.metric(lang["neg"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Negatif', na=False)]))
        col4.metric(lang["neu"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Nötr', na=False)]))
        
        st.markdown("---")
        
        # --- Grafikler ---
        grafik_kolon1, grafik_kolon2 = st.columns(2)
        
        with grafik_kolon1:
            st.subheader(lang["chart_plat"])
            st.bar_chart(filtrelenmis_df['platform'].value_counts())
            
        with grafik_kolon2:
            st.subheader(lang["chart_emo"])
            duygu_sayilari = filtrelenmis_df['duygu_durumu'].value_counts()
            fig, ax = plt.subplots(figsize=(5, 5))
            renkler = ['#2ecc71' if 'Pozitif' in e else '#e74c3c' if 'Negatif' in e else '#bdc3c7' for e in duygu_sayilari.index]
            ax.pie(duygu_sayilari, labels=duygu_sayilari.index, autopct='%1.1f%%', startangle=90, colors=renkler)
            ax.axis('equal') 
            st.pyplot(fig)
            
        st.markdown("---")
        
        # --- Kelime Bulutu ---
        st.subheader(lang["wordcloud"])
        tum_metin = " ".join(filtrelenmis_df['icerik'].dropna().astype(str).tolist())
        if len(tum_metin) > 20:
            wordcloud = WordCloud(width=800, height=300, background_color="white", max_words=100, colormap="viridis").generate(tum_metin)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)

        st.markdown("---")
        
        # --- Tablo ve Excel ---
        st.subheader(lang["table"])
        # Gösterilecek sütunlara "ulke" de eklendi
        st.dataframe(filtrelenmis_df[['created_at', 'ulke', 'platform', 'kategori', 'duygu_durumu', 'duygu_skoru', 'icerik']], use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtrelenmis_df.to_excel(writer, index=False, sheet_name='Analiz Verileri')
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label=lang["download"],
            data=buffer.getvalue(),
            file_name=f'analiz_raporu_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.warning(lang["no_data"])