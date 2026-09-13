import os
import arcpy
from arcpy.sa import *
import matplotlib.pyplot as plt

# Bu script, yangin ONCESI (Temmuz 2021) bitki ortusu yogunlugunu/sagligini (NDVI)
# hesaplar ve gercek yanma siddetiyle (dNBR) karsilastirir. Yon varsayilmaz --
# iliski veriden ne cikarsa o kullanilir (slope analizinde oldugu gibi).
# ON KOSUL: scripts/23_download_ndvi_bands.py calistirilip pre_fire_B04.tif ve
# pre_fire_south_B04.tif indirilmis olmali.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

b04_north = os.path.join(workspace, "pre_fire_B04.tif")
b04_south = os.path.join(workspace, "pre_fire_south_B04.tif")
if not (os.path.exists(b04_north) and os.path.exists(b04_south)):
    raise FileNotFoundError("Once scripts/23_download_ndvi_bands.py calistirilmali!")

print("1. Kuzey + Guney B04 mozaikleniyor...")
b04_mosaic = "pre_b04_mosaic.tif"
arcpy.management.MosaicToNewRaster(
    [b04_north, b04_south], workspace, b04_mosaic,
    pixel_type="16_BIT_UNSIGNED", number_of_bands=1,
)

print("2. NDVI hesaplaniyor: (B08 - B04) / (B08 + B04), yalnizca yanan alan sinirlarinda...")
fire_extent = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")
arcpy.env.extent = arcpy.Describe(fire_extent).extent
arcpy.env.cellSize = 20
arcpy.env.snapRaster = fire_extent

b08 = Float(Raster(os.path.join(workspace, "pre_b8_mosaic.tif")))
b04 = Float(Raster(os.path.join(workspace, b04_mosaic)))
ndvi = (b08 - b04) / (b08 + b04)
ndvi_masked = ExtractByMask(ndvi, fire_extent)
ndvi_out = os.path.join(workspace, "Pre_Fire_NDVI_Masked.tif")
ndvi_masked.save(ndvi_out)
print(f"   Kaydedildi: {ndvi_out}")

print("\n3. Dogrulama: Yanma siddeti sinifina gore ortalama YANGIN ONCESI NDVI hesaplaniyor...")
zonal_table = os.path.join(workspace, "zonal_ndvi_by_severity.dbf")
ZonalStatisticsAsTable(fire_extent, "Value", ndvi_masked, zonal_table, "DATA", "MEAN")

# NOT: dNBR_Full_Masked_Classified.tif siniflari 1'den baslar (scripts/13'teki USGS esikleri):
# 1=Yanmamis (<0.1), 2=Dusuk (0.1-0.27), 3=Orta-Dusuk (0.27-0.44), 4=Orta-Yuksek (0.44-0.66), 5=Yuksek (>0.66)
severity_labels = {1: "Yanmamis", 2: "Dusuk", 3: "Orta-Dusuk", 4: "Orta-Yuksek", 5: "Yuksek"}
results = {}
with arcpy.da.SearchCursor(zonal_table, ["Value", "MEAN", "COUNT"]) as cursor:
    for value, mean, count in cursor:
        results[int(value)] = (mean, count)

print("\n--- SONUCLAR: Yanma Siddeti Sinifina Gore Ortalama Yangin-Oncesi NDVI ---")
for k in sorted(results):
    mean, count = results[k]
    print(f"  {severity_labels.get(k, k)}: ortalama NDVI = {mean:.4f}  (piksel: {int(count)})")

keys = sorted(results)
means = [results[k][0] for k in keys]
labels = [severity_labels.get(k, str(k)) for k in keys]

plt.figure(figsize=(9, 5.5))
plt.bar(labels, means, color=["#1a9850", "#a6d96a", "#fee08b", "#fdae61", "#d73027"][: len(keys)])
plt.title("Yangin Oncesi Bitki Ortusu (NDVI) ile Gercek Yanma Siddeti Iliskisi", fontweight="bold")
plt.ylabel("Ortalama Yangin-Oncesi NDVI")
plt.xlabel("Gercek dNBR Yanma Siddeti Sinifi")
plt.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_ndvi_siddet_iliskisi.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Grafik kaydedildi: {out_png}")
arcpy.CheckInExtension("Spatial")
