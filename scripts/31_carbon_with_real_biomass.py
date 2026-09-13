import sys
import os
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")

# KARBON EMISYONU TAHMINI - GERCEK UYDU TABANLI BIYOKUTLE VERISIYLE
#
# scripts/27, biyokutleyi "50/90/130 ton/ha" gibi genel Akdeniz-ormani
# literatur araligiyla varsaymisti (IPCC "Tier 1" yontemi). Bu script,
# bunun yerine ESA CCI Biomass v6.0 (2020, 100m, uydu-tabanli, Manavgat'a
# OZGU gercek biyokutle degerleri) verisini kullanir -- "genel bir tahmin"
# yerine "bu ormana ozgu olculmus/modellenmis deger" ile hesaplama yapar.
# 2020 verisi kullanilmistir (yangindan ONCEKI son yil -- yanmadan once
# ormanin gercekte tasidigi biyokutleyi yansitir).
#
# ESA CCI Biomass urun dokumantasyonu, AGB>50 Mg/ha oldugunda hedef goreli
# hatayi %20 olarak belirtir -- bu yuzden +-%20 duyarlilik araligi da
# rastgele degil, urunun kendi belgelenmis dogruluk payidir.
#
# Yanma faktoru (Cf) hala dNBR siddet sinifina gore olceklenir (scripts/27
# ile ayni degerler) -- bu kismi olculemedik, literatur/GFED araligindan.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

true_fire = os.path.join(workspace, "dNBR_True_Fire_Only.tif")
biomass_raw = os.path.join(workspace, "esacci_agb_2020.tif")

print("1. ESA CCI Biomass (2020), gercek yangin rasterinin izgarasina hizalaniyor...")
arcpy.env.snapRaster = true_fire
arcpy.env.cellSize = true_fire
arcpy.env.extent = true_fire
biomass_utm = os.path.join(workspace, "AGB_2020_UTM.tif")
arcpy.management.ProjectRaster(biomass_raw, biomass_utm, arcpy.Describe(true_fire).spatialReference, "BILINEAR", 10)

print("2. Gercek yangin sinirina maskeleniyor...")
biomass_masked = ExtractByMask(biomass_utm, true_fire)

class_info = {2: ("Dusuk", 0.30), 3: ("Orta-Dusuk", 0.45), 4: ("Orta-Yuksek", 0.60), 5: ("Yuksek", 0.80)}

print("3. Siddet sinifina gore GERCEK ortalama biyokutle hesaplaniyor (dogrulama icin)...")
zonal_table = os.path.join(workspace, "zonal_biomass_by_severity.dbf")
ZonalStatisticsAsTable(true_fire, "Value", biomass_masked, zonal_table, "DATA", "MEAN")
biomass_by_class = {}
with arcpy.da.SearchCursor(zonal_table, ["Value", "MEAN"]) as cur:
    for value, mean in cur:
        biomass_by_class[int(value)] = mean
print("\n--- Siddet Sinifina Gore Gercek Ortalama Biyokutle (ESA CCI, ton/ha) ---")
for cls, (label, cf) in class_info.items():
    if cls in biomass_by_class:
        print(f"  {label}: {biomass_by_class[cls]:.1f} ton/ha")

print("\n4. Piksel-bazli CO2 hesabi yapiliyor (gercek biyokutle x yanma faktoru)...")
severity_arr_raw = arcpy.RasterToNumPyArray(Raster(true_fire), nodata_to_value=255)
biomass_arr_raw = arcpy.RasterToNumPyArray(biomass_masked, nodata_to_value=-1)
severity_arr = severity_arr_raw.astype(float)
biomass_arr = biomass_arr_raw.astype(float)
biomass_arr[biomass_arr < 0] = np.nan

cf_arr = np.zeros_like(severity_arr)
for cls, (label, cf) in class_info.items():
    cf_arr[severity_arr == cls] = cf

cell_area_ha = (arcpy.Raster(true_fire).meanCellWidth ** 2) / 10000.0
gef_co2 = 1.569

co2_per_pixel = biomass_arr * cell_area_ha * cf_arr * gef_co2
valid = ~np.isnan(co2_per_pixel)
total_co2_mid = np.nansum(co2_per_pixel)
total_co2_low = total_co2_mid * 0.8   # ESA CCI Biomass belgelenen goreli hata: -%20
total_co2_high = total_co2_mid * 1.2  # +%20

print(f"\n--- SONUC: Gercek Uydu-Tabanli Biyokutle ile CO2 Tahmini ---")
print(f"  Orta (ESA CCI 2020 gercek deger): {total_co2_mid:,.0f} ton CO2")
print(f"  Alt sinir (-%20, urun dogruluk payi): {total_co2_low:,.0f} ton CO2")
print(f"  Ust sinir (+%20, urun dogruluk payi): {total_co2_high:,.0f} ton CO2")

car_per_year = 4.6
tree_per_year = 0.0217
print(f"\n  ~{total_co2_mid/car_per_year:,.0f} aracin yillik emisyonuna esdeger")
print(f"  Dengelemek icin ~{total_co2_mid/tree_per_year:,.0f} olgun agacin bir yillik karbon tutumu gerekir")

print("\n5. Gorsel guncelleniyor...")
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

keys = [2, 3, 4, 5]
labels = [class_info[k][0] for k in keys]
bvals = [biomass_by_class.get(k, 0) for k in keys]
axes[0].bar(labels, bvals, color=["#1a9850", "#fee08b", "#fdae61", "#d73027"])
axes[0].set_title("Yangin Oncesi GERCEK Biyokutle\n(ESA CCI 2020, ton/ha)")
axes[0].set_ylabel("Ton/hektar")

scenario_labels = ["Alt Sinir\n(-%20)", "Gercek Deger\n(ESA CCI 2020)", "Ust Sinir\n(+%20)"]
scenario_vals = [total_co2_low, total_co2_mid, total_co2_high]
axes[1].bar(scenario_labels, scenario_vals, color=["#a6d96a", "#fd8d3c", "#d73027"])
axes[1].set_title("Tahmini CO2 Emisyonu (ton)\nGercek Uydu Biyokutlesi ile")
axes[1].set_ylabel("Ton CO2")
for i, v in enumerate(scenario_vals):
    axes[1].text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("2021 Manavgat Yangini - Karbon Emisyonu (ESA CCI Uydu Biyokutlesi ile)", fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_karbon_emisyonu.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"\n!!! TAMAMLANDI !!! Grafik guncellendi: {out_png}")
arcpy.CheckInExtension("Spatial")
