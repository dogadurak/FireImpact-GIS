import requests
import matplotlib.pyplot as plt
import datetime

print("Manavgat 2021 meteoroloji verileri indiriliyor...")

# Manavgat merkez koordinatlari
lat = 36.78
lon = 31.44
start_date = "2021-07-20"
end_date = "2021-08-10"

url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,wind_speed_10m_max,precipitation_sum&timezone=Europe%2FIstanbul"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    daily = data.get("daily", {})
    
    dates = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    wind_max = daily.get("wind_speed_10m_max", [])
    
    # Tarihleri datetime objesine cevir (sadece gun/ay)
    parsed_dates = [datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%d %b") for d in dates]

    # Grafikleri ciz
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color_temp = '#d73027'
    ax1.set_xlabel('Tarih (2021)', fontsize=12)
    ax1.set_ylabel('Maksimum Sicaklik (C)', color=color_temp, fontsize=12, fontweight='bold')
    line1 = ax1.plot(parsed_dates, temp_max, marker='o', color=color_temp, linewidth=2, label='Maksimum Sicaklik (C)')
    ax1.tick_params(axis='y', labelcolor=color_temp)
    ax1.tick_params(axis='x', rotation=45)
    
    # Ruzgar hizi icin ikinci eksen
    ax2 = ax1.twinx()  
    color_wind = '#4575b4'
    ax2.set_ylabel('Maksimum Ruzgar Hizi (km/s)', color=color_wind, fontsize=12, fontweight='bold')
    line2 = ax2.plot(parsed_dates, wind_max, marker='s', color=color_wind, linewidth=2, linestyle='--', label='Maksimum Ruzgar Hizi (km/s)')
    ax2.tick_params(axis='y', labelcolor=color_wind)

    # Yangin baslama tarihi cizgisi (28 Temmuz 2021)
    fire_start_idx = dates.index("2021-07-28")
    plt.axvline(x=fire_start_idx, color='black', linestyle=':', linewidth=2, label='Yangin Baslangici (28 Tem)')
    ax1.text(fire_start_idx + 0.2, max(temp_max), 'Yangin Baslangici', rotation=90, va='top', fontweight='bold')

    # Ortak Lejant
    lines = line1 + line2 + [plt.Line2D([0], [0], color='black', linestyle=':', linewidth=2)]
    labels = [l.get_label() for l in line1 + line2] + ['Yangin Baslangici (28 Tem)']
    ax1.legend(lines, labels, loc='upper left')

    plt.title('Manavgat Yangini Oncesi ve Sirasinda Meteorolojik Kosullar (Sıcaklık ve Rüzgar)\n*Kurak ve Ruzgarli Havanin Yangin Yayilimina Etkisi*', fontsize=14)
    fig.tight_layout()
    
    out_file = "manavgat_yangin_meteorolojisi.png"
    plt.savefig(out_file, dpi=300)
    print(f"Basarili! Meteoroloji grafigi kaydedildi: {out_file}")

else:
    print(f"Hata: API baglantisi basarisiz. Kod: {response.status_code}")
