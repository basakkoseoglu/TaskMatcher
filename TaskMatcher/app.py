from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

def verileri_yukle(dosya_adi):
    with open(dosya_adi, 'r', encoding='utf-8') as f:
        return json.load(f)

def verileri_kaydet(dosya_adi, veri):
    with open(dosya_adi, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

calisanlar = verileri_yukle('data/calisanlar.json')['calisanlar']
gorevler = verileri_yukle('data/gorevler.json')['gorevler']

def gorev_ata(gorev):
    uygun_calisan = None
    min_kapasite_kalan = float('inf')

    for calisan in calisanlar:
        if gorev['gereksinim'] in calisan['yetkinlikler']:
            atanan_gorev_suresi = sum(
                g['sure'] for g in gorevler if g.get('atanan_calisan') == calisan['isim']
            )
            kalan_kapasite = calisan['kapasite'] - atanan_gorev_suresi
            if kalan_kapasite >= gorev['sure'] and kalan_kapasite < min_kapasite_kalan:
                uygun_calisan = calisan
                min_kapasite_kalan = kalan_kapasite

    if uygun_calisan:
        gorev['atanan_calisan'] = uygun_calisan['isim']
        uygun_calisan.setdefault('gorevler', []).append(gorev)
        return uygun_calisan['isim']
    else:
        gorev['atanan_calisan'] = "Atanmadı"
        return None

def tum_gorevleri_yeniden_ata():
    for calisan in calisanlar:
        calisan['gorevler'] = []
    for gorev in gorevler:
        gorev['atanan_calisan'] = ""
    for gorev in gorevler:
        gorev_ata(gorev)

@app.route('/')
def index():
    toplam_calisan = len(calisanlar)
    toplam_kapasite = sum(c['kapasite'] for c in calisanlar)
    toplam_gorev = len(gorevler)
    atanmis_gorevler = len([g for g in gorevler if g.get('atanan_calisan') and g['atanan_calisan'] != "Atanmadı"])
    atanamamis_gorevler = toplam_gorev - atanmis_gorevler
    return render_template('index.html', toplam_calisan=toplam_calisan, toplam_kapasite=toplam_kapasite, toplam_gorev=toplam_gorev, atanmis_gorevler=atanmis_gorevler, atanamamis_gorevler=atanamamis_gorevler)

@app.route('/calisanlar')
def calisanlar_yonetimi():
    return render_template('calisanlar.html', calisanlar=calisanlar)

@app.route('/gorevler')
def gorevler_yonetimi():
    return render_template('gorevler.html', gorevler=gorevler)

@app.route('/calisan_ekle', methods=['GET', 'POST'])
def calisan_ekle():
    if request.method == 'POST':
        yeni_calisan = {
            "isim": request.form['isim'],
            "kapasite": int(request.form['kapasite']),
            "yetkinlikler": request.form['yetkinlikler'].split(',')
        }
        calisanlar.append(yeni_calisan)
        verileri_kaydet('data/calisanlar.json', {"calisanlar": calisanlar})
        return redirect(url_for('calisanlar_yonetimi'))
    return render_template('calisan_ekle.html')

@app.route('/gorev_ekle', methods=['GET', 'POST'])
def gorev_ekle():
    if request.method == 'POST':
        yeni_gorev = {
            "isim": request.form['isim'],
            "sure": int(request.form['sure']),
            "gereksinim": request.form['gereksinim'],
            "atanan_calisan": ""
        }
        gorevler.append(yeni_gorev)
        tum_gorevleri_yeniden_ata()
        verileri_kaydet('data/gorevler.json', {"gorevler": gorevler})
        return redirect(url_for('gorevler_yonetimi'))
    return render_template('gorev_ekle.html')

@app.route('/gorev_atama')
def gorev_atama_sayfasi():
    tum_gorevleri_yeniden_ata()
    verileri_kaydet('data/gorevler.json', {"gorevler": gorevler})
    return render_template('gorev_atama.html', gorevler=gorevler)

if __name__ == '__main__':
    app.run(debug=True)
