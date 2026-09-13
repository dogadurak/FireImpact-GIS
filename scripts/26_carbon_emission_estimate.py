import os
import arcpy
import numpy as np
import matplotlib.pyplot as plt

# KARBON EMISYONU TAHMINI (kaba, literatur temelli tahmin - olculmemis!)
#
# Yontem: IPCC 2006 Ulusal Sera Gazi Envanterleri Kilavuzu, Cilt 4 (AFOLU),
# Bolum 2, Denklem 2.14:
#     L_fire = A x MB x Cf x Gef x 10^-3
# Burada:
#   A   = yanan alan (ha)
#   MB  = yanma icin mevcut biyokutle (ton/ha, kuru madde)
#   Cf  = yanma faktoru (0-1, yakitin ne kadarinin fiilen yandigi)
#   Gef = emisyon faktoru (g CO2 / kg kuru madde)
#
# dNBR siddet sinifi, yanmanin ne kadar TAM oldugunun (combustion completeness)
# dogrudan bir gostergesidir (Key & Benson 2006, USGS FIREMON). Bu yuzden Cf,
# siddet sinifina gore olceklendirilmistir (IPCC 2006 Tablo 2.6 ve van der Werf
# ve ark. 2010 GFED calismalarindaki 0.2-0.8 araligi ile tutarli).
#
# MB (biyokutle) icin Akdeniz ibrelli orman literaturunde genis bir aralik
# oldugundan (yaklasik 50-130 ton/ha), TEK bir sahte-kesin sayi yerine
# DUSUK / ORTA / YUKSEK senaryo olarak raporlanmistir.
#
# Gef(CO2) = 1569 g/kg -- IPCC 2006 AFOLU Tablo 2.5, "Extratropical forest" varsayilani.
#
# NOT: Bu bir saha olcumu DEGILDIR, yayinlanmis literatur referans degerleriyle
# yapilan bir yaklasik hesaptir. StoryMap'te "tahmini" ibaresiyle sunulmalidir.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
dnbr_path = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")

r = arcpy.Raster(dnbr_path)
cell_area_ha = (r.meanCellWidth * r.meanCellHeight) / 10000.0
print(f"Piksel boyutu: {r.meanCellWidth}m x {r.meanCellHeight}m -> {cell_area_ha:.4f} ha/piksel")

arr = arcpy.RasterToNumPyArray(r, nodata_to_value=255)
values, counts = np.unique(arr, return_counts=True)
area_by_class = {int(v): c * cell_area_ha for v, c in zip(values, counts) if v != 255}

class_info = {
    # sinif: (etiket, yanma faktoru Cf)
    1: ("Yanmamis", 0.0),
    2: ("Dusuk", 0.30),
    3: ("Orta-Dusuk", 0.45),
    4: ("Orta-Yuksek", 0.60),
    5: ("Yuksek", 0.80),
}
biomass_scenarios = {"Dusuk Biyokutle Senaryosu": 50.0, "Orta Biyokutle Senaryosu": 90.0, "Yuksek Biyokutle Senaryosu": 130.0}
gef_co2 = 1.569  # ton CO2 / ton kuru madde (1569 g/kg)

print("\n--- Siddet Sinifina Gore Yanan Alan ---")
total_burned_ha = 0.0
for cls, (label, cf) in class_info.items():
    area_ha = area_by_class.get(cls, 0.0)
    print(f"  {label}: {area_ha:,.1f} ha")
    if cls != 1:
        total_burned_ha += area_ha
print(f"  TOPLAM YANAN ALAN (Dusuk+Orta-Dusuk+Orta-Yuksek+Yuksek): {total_burned_ha:,.1f} ha")

print("\n--- CO2 Emisyon Tahmini (Senaryo Bazinda) ---")
scenario_totals = {}
for scenario_name, mb in biomass_scenarios.items():
    total_co2 = 0.0
    for cls, (label, cf) in class_info.items():
        if cls == 1:
            continue
        area_ha = area_by_class.get(cls, 0.0)
        co2 = area_ha * mb * cf * gef_co2
        total_co2 += co2
    scenario_totals[scenario_name] = total_co2
    print(f"  {scenario_name} (MB={mb} ton/ha): {total_co2:,.0f} ton CO2")

mid_co2 = scenario_totals["Orta Biyokutle Senaryosu"]
low_co2 = scenario_totals["Dusuk Biyokutle Senaryosu"]
high_co2 = scenario_totals["Yuksek Biyokutle Senaryosu"]

# Karsilastirma istatistikleri (kaynak belirtilerek)
car_per_year = 4.6  # ton CO2/yil, ABD EPA "tipik binek arac" ortalamasi
tree_per_year = 0.0217  # ton CO2/yil, ortalama olgun agac (EPA/arborday.org)

print("\n--- Anlasilir Karsilastirmalar (Orta Senaryo Uzerinden) ---")
print(f"  ~{mid_co2 / car_per_year:,.0f} adet binek aracin YILLIK emisyonuna esdeger (EPA ortalamasi: {car_per_year} ton CO2/yil/arac)")
print(f"  Bunu dengelemek icin ~{mid_co2 / tree_per_year:,.0f} olgun agacin BIR YIL boyunca karbon tutmasi gerekir")

print("\n--- Gorsel Olusturuluyor ---")
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

labels = [class_info[c][0] for c in [2, 3, 4, 5]]
areas = [area_by_class.get(c, 0.0) for c in [2, 3, 4, 5]]
axes[0].bar(labels, areas, color=["#1a9850", "#fee08b", "#fdae61", "#d73027"])
axes[0].set_title("Siddet Sinifina Gore Yanan Alan (ha)")
axes[0].set_ylabel("Alan (hektar)")

scenario_names = list(scenario_totals.keys())
scenario_vals = list(scenario_totals.values())
axes[1].bar(["Dusuk\nSenaryo", "Orta\nSenaryo", "Yuksek\nSenaryo"], scenario_vals, color=["#a6d96a", "#fdae61", "#d73027"])
axes[1].set_title("Tahmini CO2 Emisyonu (ton)\n(Literatur bazli yaklasik hesap)")
axes[1].set_ylabel("Ton CO2")
for i, v in enumerate(scenario_vals):
    axes[1].text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("2021 Manavgat Yangini - Tahmini Karbon Emisyonu (IPCC 2006 AFOLU yontemi)", fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_karbon_emisyonu.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Grafik kaydedildi: {out_png}")
