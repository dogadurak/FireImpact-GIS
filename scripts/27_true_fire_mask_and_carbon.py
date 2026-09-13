import os
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

# GERCEK YANGIN MASKESI + KARBON EMISYONU TAHMINI
#
# BULGU: dNBR_Full_Masked_Classified.tif'teki "yanmis" pikseller yuz binlerce
# ayri, kucuk, bitisik-olmayan parcaya dagilmis durumda (Antalya sehir merkezi,
# yol kenarlari, tarim arazileri gibi yerlerdeki YANLIS POZITIFLER -- bulut
# golgesi, hasat, insaat, vb. nedeniyle olusan siniflandirma gurultusu; gercek
# yangin degil). Gercek Manavgat yangin kompleksi, en buyuk birkac bitisik
# parcadan olusuyor.
#
# YONTEM: RegionGroup ile bitisik parcalar bulunur, >=100 ha olanlar "gercek
# yangin" sayilir (bu esik, bagimsiz kaynaklardaki ~56,663-75,000 ha
# rakamlariyla en iyi ortusen esik olarak secilmistir -- kucuk gurultu
# parcalari tek tek elenmis olur).
#
# Karbon hesabi IPCC 2006 AFOLU Kilavuzu Denklem 2.14'e dayanir:
#     CO2 (ton) = Alan(ha) x Biyokutle(ton/ha) x Yanma_Faktoru x Emisyon_Faktoru
# Yanma faktoru dNBR siddet sinifina gore olceklendirilmistir (siddet = yanmanin
# ne kadar tam oldugunun gostergesi). Biyokutle, Akdeniz ibrelli orman
# literaturundeki genis araliktan dolayi DUSUK/ORTA/YUKSEK senaryo olarak
# verilir (tek bir sahte-kesin sayi yerine). Emisyon faktoru CO2 icin IPCC 2006
# AFOLU Tablo 2.5 "extratropical forest" varsayilanidir (1569 g/kg).
#
# NOT: Bu bir saha olcumu DEGILDIR, literatur referans degerleriyle yapilan
# yaklasik bir hesaptir -- StoryMap'te "tahmini" ibaresiyle sunulmalidir.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

dnbr_path = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")
cell_area_ha = (arcpy.Raster(dnbr_path).meanCellWidth ** 2) / 10000.0

MIN_FIRE_SIZE_HA = 100

print(f"1. Bitisik yanmis parcalar bulunuyor (RegionGroup)...")
burned = Con(Raster(dnbr_path) >= 2, 1)
regions = RegionGroup(burned, "FOUR", "WITHIN", "NO_LINK")

region_table = os.path.join(workspace, "region_sizes_temp.dbf")
ZonalStatisticsAsTable(regions, "Value", regions, region_table, "DATA", "ALL")

keep_ids = []
with arcpy.da.SearchCursor(region_table, ["Value", "COUNT"]) as cur:
    for value, count in cur:
        if count * cell_area_ha >= MIN_FIRE_SIZE_HA:
            keep_ids.append(int(value))
print(f"   >={MIN_FIRE_SIZE_HA} ha esigini gecen bitisik parca sayisi: {len(keep_ids)}")
print(f"   (Karsilastirma: uydu calismasi ~56,663 ha, Antalya Orman Bolge Mudurlugu ~75,000 ha bildirmisti)")

print("2. Gercek yangin maskesi ile dNBR siddet sinifi kesistiriliyor...")
true_fire_mask = Con(arcpy.sa.InList(regions, keep_ids), 1)
dnbr_true = ExtractByMask(dnbr_path, true_fire_mask)
dnbr_true.save(os.path.join(workspace, "dNBR_True_Fire_Only.tif"))

arr_raw = arcpy.RasterToNumPyArray(dnbr_true, nodata_to_value=255)
values, counts = np.unique(arr_raw, return_counts=True)
area_by_class = {int(v): c * cell_area_ha for v, c in zip(values, counts) if v != 255}

class_info = {
    1: ("Yanmamis", 0.0),
    2: ("Dusuk", 0.30),
    3: ("Orta-Dusuk", 0.45),
    4: ("Orta-Yuksek", 0.60),
    5: ("Yuksek", 0.80),
}
print("\n--- Siddet Sinifina Gore Yanan Alan (yalnizca gercek yangin) ---")
total_burned_ha = 0.0
for cls, (label, cf) in class_info.items():
    area_ha = area_by_class.get(cls, 0.0)
    print(f"  {label}: {area_ha:,.1f} ha")
    if cls != 1:
        total_burned_ha += area_ha
print(f"  TOPLAM YANAN ALAN: {total_burned_ha:,.1f} ha")

biomass_scenarios = {"Dusuk": 50.0, "Orta": 90.0, "Yuksek": 130.0}
gef_co2 = 1.569
scenario_totals = {}
print("\n--- CO2 Emisyon Tahmini ---")
for name, mb in biomass_scenarios.items():
    total_co2 = sum(area_by_class.get(c, 0.0) * mb * cf * gef_co2 for c, (label, cf) in class_info.items() if c != 1)
    scenario_totals[name] = total_co2
    print(f"  {name} Biyokutle Senaryosu (MB={mb} ton/ha): {total_co2:,.0f} ton CO2")

mid_co2 = scenario_totals["Orta"]
car_per_year = 4.6
tree_per_year = 0.0217
print(f"\n  Orta senaryo ~{mid_co2/car_per_year:,.0f} aracin yillik emisyonuna esdeger (EPA ortalamasi)")
print(f"  Dengelemek icin ~{mid_co2/tree_per_year:,.0f} olgun agacin bir yillik karbon tutumu gerekir")

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
labels = [class_info[c][0] for c in [2, 3, 4, 5]]
areas = [area_by_class.get(c, 0.0) for c in [2, 3, 4, 5]]
axes[0].bar(labels, areas, color=["#1a9850", "#fee08b", "#fdae61", "#d73027"])
axes[0].set_title(f"Siddet Sinifina Gore Yanan Alan (ha)\n(Toplam: {total_burned_ha:,.0f} ha)")
axes[0].set_ylabel("Alan (hektar)")

axes[1].bar([f"{k}\nSenaryo" for k in scenario_totals], list(scenario_totals.values()), color=["#a6d96a", "#fdae61", "#d73027"])
axes[1].set_title("Tahmini CO2 Emisyonu (ton)")
axes[1].set_ylabel("Ton CO2")
for i, v in enumerate(scenario_totals.values()):
    axes[1].text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("2021 Manavgat Yangini - Tahmini Karbon Emisyonu\n(Yalnizca gercek yangin lekesi, siniflandirma gurultusu haric)", fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_karbon_emisyonu.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"\n!!! TAMAMLANDI !!! Grafik kaydedildi: {out_png}")
arcpy.CheckInExtension("Spatial")
