import sqlite3

def kontrol_et():
    conn = sqlite3.connect('turkiye_veri_agi.db')
    cursor = conn.cursor()
    # Son 10 veride ortalama duygu -0.5 altındaysa alarm ver
    cursor.execute("SELECT duygu_skoru FROM sosyal_medya_akis ORDER BY id DESC LIMIT 10")
    skorlar = [x[0] for x in cursor.fetchall()]
    if skorlar and (sum(skorlar)/len(skorlar) < -0.5):
        print("⚠️ KRİTİK ALARM: Sosyal ağlarda negatif duygu yoğunluğu saptandı!")
    conn.close()