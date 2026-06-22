from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Veritabanı bağlantı fonksiyonu
def get_db_connection():
    conn = sqlite3.connect('turkiye_veri_agi.db')
    conn.row_factory = sqlite3.Row  # Verileri sözlük gibi kullanabilmek için
    return conn

@app.route('/')
def ana_sayfa():
    try:
        conn = get_db_connection()
        # 'sosyal_medya_akis' tablosundan son 300 veriyi çekelim
        veriler = conn.execute('SELECT * FROM sosyal_medya_akis ORDER BY id DESC LIMIT 300').fetchall()
        conn.close()
        baglanti_durumu = "Başarılı"
    except Exception as e:
        veriler = []
        baglanti_durumu = f"Hata: {e}"

    return render_template('index.html', 
                           sayfa_basligi="Web ve Sosyal Medya Analizi Merkezi",
                           veriler=veriler,
                           baglanti_durumu=baglanti_durumu)

if __name__ == '__main__':
    app.run(debug=True, port=5000)