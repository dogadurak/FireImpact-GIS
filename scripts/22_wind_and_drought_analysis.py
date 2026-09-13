import requests
import datetime
import math
import os
import numpy as np
import matplotlib.pyplot as plt
import arcpy

# Bu script iki seyi yapar:
# 1) Yangin oncesi ~7 aylik kumulatif yagisi hesaplayip gercek bir "kuraklik birikimi" gostergesi uretir.
# 2) Yangin gunlerindeki baskin ruzgar yonunu hesaplayip dNBR haritasi uzerine ok olarak bindirir.

lat, lon = 36.78, 31.44
start_date = "2021-01-01"
end_date = "2021-08-10"
fire_start = "2021-07-28"
fire_end = "2021-08-10"

print("1. Open-Meteo'dan gunluk meteoroloji verisi cekiliyor (Ocak-Agustos 2021)...")
url = (
    f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
    f"&start_date={start_date}&end_date={end_date}"
    f"&daily=precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,temperature_2m_max"
    f"&timezone=Europe%2FIstanbul"
)
resp = requests.get(url, timeout=30)
resp.raise_for_status()
daily = resp.json()["daily"]

dates = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in daily["time"]]
precip = np.array(daily["precipitation_sum"], dtype=float)
wind_speed = np.array(daily["wind_speed_10m_max"], dtype=float)
wind_dir = np.array(daily["wind_direction_10m_dominant"], dtype=float)

cum_precip = np.cumsum(np.nan_to_num(precip))
fire_start_idx = daily["time"].index(fire_start)

# Yangindan onceki son yagisli gunden itibaren gecen sure
last_rain_idx = None
for i in range(fire_start_idx, -1, -1):
    if precip[i] and precip[i] > 1.0:
        last_rain_idx = i
        break
days_dry = fire_start_idx - last_rain_idx if last_rain_idx is not None else fire_start_idx
print(f"   -> Yangin basladiginda, son 1mm+ yagistan bu yana gecen sure: {days_dry} gun")
print(f"   -> Yangin baslangicina kadar toplam (Ocak-Temmuz) yagis: {cum_precip[fire_start_idx]:.1f} mm")

print("1b. Bilimsel dogruluk kontrolu: 2021 yazi, Akdeniz ikliminde normal bir yaz kuraklamasi mi")
print("    yoksa gecmis yillara gore ANORMAL bir kuraklik/sicaklik mi? (2015-2020 baz alinarak)")
baseline_window = ("06-01", "08-10")
baseline_years = range(2015, 2021)
base_temps, base_precips = [], []
for yr in baseline_years:
    b_url = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
        f"&start_date={yr}-{baseline_window[0]}&end_date={yr}-{baseline_window[1]}"
        f"&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FIstanbul"
    )
    b_resp = requests.get(b_url, timeout=30)
    b_resp.raise_for_status()
    b_daily = b_resp.json()["daily"]
    base_temps.append(np.nanmean(b_daily["temperature_2m_max"]))
    base_precips.append(np.nansum(b_daily["precipitation_sum"]))

baseline_temp_mean = float(np.mean(base_temps))
baseline_precip_mean = float(np.mean(base_precips))

window_2021_mask = (np.array(dates) >= datetime.datetime(2021, 6, 1)) & (np.array(dates) <= datetime.datetime(2021, 8, 10))
temp_2021_window = np.nanmean(np.array(daily["temperature_2m_max"])[window_2021_mask])
precip_2021_window = np.nansum(precip[window_2021_mask])

temp_anomaly = temp_2021_window - baseline_temp_mean
precip_anomaly = precip_2021_window - baseline_precip_mean
print(f"   -> 2015-2020 ortalamasi (1 Haz-10 Agu): Sicaklik {baseline_temp_mean:.1f} C, Yagis {baseline_precip_mean:.1f} mm")
print(f"   -> 2021 ayni donem: Sicaklik {temp_2021_window:.1f} C, Yagis {precip_2021_window:.1f} mm")
print(f"   -> ANOMALI: Sicaklik {temp_anomaly:+.1f} C, Yagis {precip_anomaly:+.1f} mm (6 yillik baza gore)")

print("2. Yangin gunlerindeki (28 Tem - 10 Agu) baskin ruzgar yonu hesaplaniyor...")
fire_mask = (np.array(dates) >= datetime.datetime.strptime(fire_start, "%Y-%m-%d")) & \
            (np.array(dates) <= datetime.datetime.strptime(fire_end, "%Y-%m-%d"))
dirs_rad = np.deg2rad(wind_dir[fire_mask])
speeds = wind_speed[fire_mask]
# Vektorel (agirlikli) ortalama ruzgar yonu.
# wind_direction_10m_dominant, ruzgarin ESTIGI yonu verir (meteorolojik konvansiyon,
# 0=Kuzeyden esen ruzgar). Bearing -> birim vektor: x=sin(teta), y=cos(teta).
x = np.sum(speeds * np.sin(dirs_rad))
y = np.sum(speeds * np.cos(dirs_rad))
dominant_from_deg = (math.degrees(math.atan2(x, y)) + 360) % 360
dominant_to_deg = (dominant_from_deg + 180) % 360  # ruzgarin GITTIGI (yayilma) yonu

compass = ["K", "KKD", "KD", "DKD", "D", "DGD", "GD", "GGD", "G", "GGB", "GB", "BGB", "B", "BKB", "KB", "KKB"]


def to_compass(deg):
    idx = int((deg / 22.5) + 0.5) % 16
    return compass[idx]


print(f"   -> Ruzgarin estigi yon: {dominant_from_deg:.0f} derece ({to_compass(dominant_from_deg)})")
print(f"   -> Muhtemel yangin yayilma yonu: {dominant_to_deg:.0f} derece ({to_compass(dominant_to_deg)})")

print("3. dNBR haritasi arka plan olarak hazirlaniyor...")
workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
dnbr_path = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")
arr_raw = arcpy.RasterToNumPyArray(arcpy.Raster(dnbr_path), nodata_to_value=255)
arr = arr_raw.astype(float)
arr[arr == 255] = np.nan

print("4. Gorsel olusturuluyor...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].plot(dates, cum_precip, color="#4575b4", linewidth=2)
axes[0].axvline(dates[fire_start_idx], color="#d73027", linestyle=":", linewidth=2, label="Yangin Baslangici (28 Tem)")
axes[0].set_title("2021 Kumulatif Yagis ve Kuraklik Birikimi\n(Manavgat)", fontweight="bold")
axes[0].set_ylabel("Kumulatif Yagis (mm)")
axes[0].set_xlabel("Tarih")
axes[0].tick_params(axis="x", rotation=30)
axes[0].legend(loc="upper left")
axes[0].text(
    dates[fire_start_idx], cum_precip[fire_start_idx] * 0.5,
    f"Son yagistan bu yana\n{days_dry} gun kurak", color="#d73027", fontweight="bold", ha="right",
)

axes[1].imshow(arr, cmap="RdYlGn_r")
axes[1].axis("off")
axes[1].set_title(f"dNBR Uzerinde Baskin Ruzgar Yonu\n(Yayilma yonu: {to_compass(dominant_to_deg)})", fontweight="bold")

h, w = arr.shape
cx, cy = w * 0.5, h * 0.5
L = min(h, w) * 0.25
dx = L * math.sin(math.radians(dominant_to_deg))
dy = -L * math.cos(math.radians(dominant_to_deg))  # goruntude yukari = -y
axes[1].annotate(
    "", xy=(cx + dx, cy + dy), xytext=(cx - dx, cy - dy),
    arrowprops=dict(facecolor="black", edgecolor="white", width=6, headwidth=18, headlength=18),
)
axes[1].text(cx - dx, cy - dy - 20, "Ruzgar", color="black", fontweight="bold", ha="center",
             bbox=dict(facecolor="white", alpha=0.7, boxstyle="round"))

fig.suptitle("Meteorolojik Baglam: Kuraklik Birikimi ve Ruzgarin Yangina Etkisi", fontsize=14, fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_ruzgar_kuraklik_analizi.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Gorsel kaydedildi: {out_png}")
print("NOT: Ok, gorunti uzerinde kabaca kuzeyin yukarida oldugu varsayimiyla cizilmistir")
print("     (genel egilim gostergesi olarak; piksel-hassas bir vektor alani degildir).")
