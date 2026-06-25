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
        "country_select": "🗺️ Ülke",
        "plat_select": "🌍 Platform",
        "cat_select": "📂 Konu",
        "all_countries": "Tüm Dünya",
        "all_plats": "Tüm Platformlar",
        "all_cats": "Tüm Konular",
        "total": "📌 Toplam Çekilen Veri",
        "pos": "🟢 Pozitif İçerik",
        "neg": "🔴 Negatif İçerik",
        "neu": "⚪ Nötr İçerik",
        "chart_plat": "📊 Platform Dağılımı",
        "chart_cat": "📂 Konu Dağılımı",
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
        "country_select": "🗺️ Country",
        "plat_select": "🌍 Platform",
        "cat_select": "📂 Topic",
        "all_countries": "Whole World",
        "all_plats": "All Platforms",
        "all_cats": "All Topics",
        "total": "📌 Total Data",
        "pos": "🟢 Positive Content",
        "neg": "🔴 Negative Content",
        "neu": "⚪ Neutral Content",
        "chart_plat": "📊 Platform Distribution",
        "chart_cat": "📂 Topic Distribution",
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
        "country_select": "🗺️ Land",
        "plat_select": "🌍 Plattform",
        "cat_select": "📂 Thema",
        "all_countries": "Ganze Welt",
        "all_plats": "Alle Plattformen",
        "all_cats": "Alle Themen",
        "total": "📌 Gesamtdaten",
        "pos": "🟢 Positiver Inhalt",
        "neg": "🔴 Negativer Inhalt",
        "neu": "⚪ Neutraler Inhalt",
        "chart_plat": "📊 Plattformverteilung",
        "chart_cat": "📂 Themenverteilung",
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
        "country_select": "🗺️ Pays",
        "plat_select": "🌍 Plateforme",
        "cat_select": "📂 Sujet",
        "all_countries": "Monde Entier",
        "all_plats": "Toutes les Plateformes",
        "all_cats": "Tous les Sujets",
        "total": "📌 Données Totales",
        "pos": "🟢 Contenu Positif",
        "neg": "🔴 Contenu Négatif",
        "neu": "⚪ Contenu Neutre",
        "chart_plat": "📊 Distribution des Plateformes",
        "chart_cat": "📂 Distribution des Sujets",
        "chart_emo": "🎯 Distribution des Sentiments",
        "wordcloud": "☁️ Mots les plus fréquents",
        "table": "🔍 Données en direct filtrées",
        "download": "📥 Télécharger en Excel",
        "no_filter": "Aucune donnée trouvée pour ces filtres.",
        "no_data": "Aucune donnée dans la base de données."
    },
    "中文": {
        "title": "网络和社交媒体分析",
        "lang_select": "🌐 语言",
        "country_select": "🗺️ 国家",
        "plat_select": "🌍 平台",
        "cat_select": "📂 主题",
        "all_countries": "全世界",
        "all_plats": "所有平台",
        "all_cats": "所有主题",
        "total": "📌 提取的数据总数",
        "pos": "🟢 正面内容",
        "neg": "🔴 负面内容",
        "neu": "⚪ 中立内容",
        "chart_plat": "📊 平台分布",
        "chart_cat": "📂 主题分布",
        "chart_emo": "🎯 情绪分布",
        "wordcloud": "☁️ 最常出现的词",
        "table": "🔍 过滤后的实时数据",
        "download": "📥 下载为 Excel 表格",
        "no_filter": "未找到符合所选过滤器的数据。",
        "no_data": "数据库中尚无数据。"
    },
    "العربية": {
        "title": "تحليل الويب ووسائل التواصل الاجتماعي",
        "lang_select": "🌐 اللغة",
        "country_select": "🗺️ الدولة",
        "plat_select": "🌍 المنصة",
        "cat_select": "📂 الموضوع",
        "all_countries": "جميع أنحاء العالم",
        "all_plats": "جميع المنصات",
        "all_cats": "جميع المواضيع",
        "total": "📌 إجمالي البيانات",
        "pos": "🟢 محتوى إيجابي",
        "neg": "🔴 محتوى سلبي",
        "neu": "⚪ محتوى محايد",
        "chart_plat": "📊 توزيع المنصات",
        "chart_cat": "📂 توزيع المواضيع",
        "chart_emo": "🎯 توزيع المشاعر",
        "wordcloud": "☁️ الكلمات الأكثر تكراراً",
        "table": "🔍 البيانات الحية المفلترة",
        "download": "📥 تحميل كملف Excel",
        "no_filter": "لم يتم العثور على بيانات.",
        "no_data": "لا توجد بيانات."
    }
}

# Sabit Listeler
TUM_PLATFORMLAR = ["Google", "Bing", "Yahoo", "Facebook", "YouTube", "X (Twitter)", "Telegram", "Instagram", "TikTok", "WhatsApp"]
ULKELER = ["Türkiye", "ABD", "Almanya", "İngiltere", "Fransa", "Rusya", "Çin", "Japonya", "Güney Kore", "İtalya", "Brezilya", "Hindistan", "Mısır", "Suudi Arabistan"]

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Web ve Sosyal Medya Analizi", page_icon="🌍", layout="wide")

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
        # LİMİTİ 500'DEN 5000'E ÇIKARDIK
        response = supabase.table("sosyal_medya_akis").select("*").order("created_at", desc=True).limit(5000).execute()
        df = pd.DataFrame(response.data)
        if not df.empty and 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            if 'ulke' not in df.columns:
                df['ulke'] = "Türkiye"
                
        return df
    except:
        return pd.DataFrame()

df = veri_getir()

if not df.empty:
    st.sidebar.markdown("---")
    
    # Ülke Menüsü
    ulke_secenekleri = [lang["all_countries"]] + ULKELER
    secilen_ulke = st.sidebar.selectbox(lang["country_select"], options=ulke_secenekleri)

    # Platform Menüsü
    platform_secenekleri = [lang["all_plats"]] + TUM_PLATFORMLAR
    secilen_platform = st.sidebar.selectbox(lang["plat_select"], options=platform_secenekleri)
    
    # Kategori Menüsü
    kategori_secenekleri = [lang["all_cats"]] + list(df['kategori'].unique())
    secilen_kategori = st.sidebar.selectbox(lang["cat_select"], options=kategori_secenekleri)
    
    # --- FİLTRELEME MANTIĞI ---
    filtrelenmis_df = df.copy()
    
    if secilen_ulke != lang["all_countries"]:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['ulke'] == secilen_ulke]
        
    if secilen_platform != lang["all_plats"]:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['platform'] == secilen_platform]
        
    if secilen_kategori != lang["all_cats"]:
        filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['kategori'] == secilen_kategori]
    
    # --- EKRAN GÖRÜNÜMÜ ---
    if filtrelenmis_df.empty:
        st.warning(lang["no_filter"])
    else:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(lang["total"], len(filtrelenmis_df))
        col2.metric(lang["pos"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Pozitif', na=False)]))
        col3.metric(lang["neg"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Negatif', na=False)]))
        col4.metric(lang["neu"], len(filtrelenmis_df[filtrelenmis_df['duygu_durumu'].str.contains('Nötr', na=False)]))
        
        st.markdown("---")
        
        # 1. SATIR GRAFİKLERİ: Platform ve Kategori
        grafik_kolon1, grafik_kolon2 = st.columns(2)
        
        with grafik_kolon1:
            st.subheader(lang["chart_plat"])
            st.bar_chart(filtrelenmis_df['platform'].value_counts())
            
        with grafik_kolon2:
            st.subheader(lang["chart_cat"])
            st.bar_chart(filtrelenmis_df['kategori'].value_counts())
            
        st.markdown("---")
        
        # 2. SATIR GRAFİKLERİ: Duygu ve Kelime Bulutu
        grafik_kolon3, grafik_kolon4 = st.columns(2)
        
        with grafik_kolon3:
            st.subheader(lang["chart_emo"])
            duygu_sayilari = filtrelenmis_df['duygu_durumu'].value_counts()
            fig, ax = plt.subplots(figsize=(5, 5))
            renkler = ['#2ecc71' if 'Pozitif' in e else '#e74c3c' if 'Negatif' in e else '#bdc3c7' for e in duygu_sayilari.index]
            ax.pie(duygu_sayilari, labels=duygu_sayilari.index, autopct='%1.1f%%', startangle=90, colors=renkler)
            ax.axis('equal') 
            st.pyplot(fig)
            
        with grafik_kolon4:
            st.subheader(lang["wordcloud"])
            tum_metin = " ".join(filtrelenmis_df['icerik'].dropna().astype(str).tolist())
            if len(tum_metin) > 20:
                wordcloud = WordCloud(width=800, height=300, background_color="white", max_words=100, colormap="viridis").generate(tum_metin)
                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wordcloud, interpolation="bilinear")
                ax_wc.axis("off")
                st.pyplot(fig_wc)

        st.markdown("---")
        
        st.subheader(lang["table"])
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