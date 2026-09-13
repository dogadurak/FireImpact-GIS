import os
import arcpy
from arcpy.sa import *
import matplotlib.pyplot as plt

# scripts/21 ve 24, dogrulamalarini dNBR_Full_Masked_Classified.tif uzerinden
# yapmisti -- bu rasterin siniflandirma gurultusu (Antalya sehir merkezi, yol
# kenarlari, tarim arazileri gibi yerlerdeki yanlis pozitifler) icerdigi
# scripts/27'de ortaya cikti. Bu script, ayni iki dogrulamayi TEMIZ yangin
# maskesiyle (dNBR_True_Fire_Only.tif, scripts/27 tarafindan uretildi) tekrarlar.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

true_fire = os.path.join(workspace, "dNBR_True_Fire_Only.tif")
if not os.path.exists(true_fire):
    raise FileNotFoundError("Once scripts/27_true_fire_mask_and_carbon.py calistirilmali!")

dnbr_scientific_path = os.path.join(workspace, "dNBR_Scientific.tif")
ndvi_full_path = os.path.join(workspace, "Pre_Fire_NDVI_Full.tif")

utm36n = arcpy.SpatialReference(32636)

print("=== 1/2: Egim/Baki dogrulamasi (temiz maske ile) ===")
slope_utm = os.path.join(workspace, "_slope_utm_tmp.tif")
aspect_utm = os.path.join(workspace, "_aspect_utm_tmp.tif")
arcpy.management.ProjectRaster(os.path.join(workspace, "Manavgat_Slope.tif"), slope_utm, utm36n, "BILINEAR", 20)
arcpy.management.ProjectRaster(os.path.join(workspace, "Manavgat_Aspect.tif"), aspect_utm, utm36n, "NEAREST", 20)

slope_reclass = Reclassify(Raster(slope_utm), "Value", RemapRange([[0, 15, 1], [15, 30, 2], [30, 90, 3]]))
aspect_reclass = Reclassify(Raster(aspect_utm), "Value",
                             RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))

slope_masked = ExtractByMask(slope_reclass, true_fire)
aspect_masked = ExtractByMask(aspect_reclass, true_fire)

slope_table = os.path.join(workspace, "zonal_slope_v2.dbf")
aspect_table = os.path.join(workspace, "zonal_aspect_v2.dbf")
ZonalStatisticsAsTable(slope_masked, "Value", Raster(dnbr_scientific_path), slope_table, "DATA", "MEAN")
ZonalStatisticsAsTable(aspect_masked, "Value", Raster(dnbr_scientific_path), aspect_table, "DATA", "MEAN")


def read_table(path):
    result = {}
    with arcpy.da.SearchCursor(path, ["Value", "MEAN", "COUNT"]) as cursor:
        for value, mean, count in cursor:
            result[int(value)] = (mean, count)
    return result


slope_stats = read_table(slope_table)
aspect_stats = read_table(aspect_table)
slope_labels = {1: "Duz/Az Egimli", 2: "Orta Egimli", 3: "Dik"}
aspect_labels = {1: "Kuzey Baki", 2: "Dogu/Bati Baki", 3: "Guney Baki"}

print("Egim sinifina gore ortalama dNBR (temiz maske):")
for k in sorted(slope_stats):
    print(f"  {slope_labels.get(k,k)}: {slope_stats[k][0]:.4f}  (piksel: {int(slope_stats[k][1])})")
print("Baki sinifina gore ortalama dNBR (temiz maske):")
for k in sorted(aspect_stats):
    print(f"  {aspect_labels.get(k,k)}: {aspect_stats[k][0]:.4f}  (piksel: {int(aspect_stats[k][1])})")

print("\n=== 2/2: NDVI-siddet dogrulamasi (temiz maske ile) ===")
ndvi_table = os.path.join(workspace, "zonal_ndvi_v2.dbf")
ZonalStatisticsAsTable(true_fire, "Value", Raster(ndvi_full_path), ndvi_table, "DATA", "MEAN")
severity_labels = {1: "Yanmamis", 2: "Dusuk", 3: "Orta-Dusuk", 4: "Orta-Yuksek", 5: "Yuksek"}
ndvi_stats = read_table(ndvi_table)
print("Siddet sinifina gore ortalama yangin-oncesi NDVI (temiz maske):")
for k in sorted(ndvi_stats):
    print(f"  {severity_labels.get(k,k)}: {ndvi_stats[k][0]:.4f}  (piksel: {int(ndvi_stats[k][1])})")

print("\nGorseller uretiliyor...")
fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

keys_s = sorted(slope_stats)
axes[0].bar([slope_labels[k] for k in keys_s], [slope_stats[k][0] for k in keys_s], color=["#1a9850", "#fdae61", "#d73027"])
axes[0].set_title("Egim -> Ortalama dNBR\n(Temiz Maske)")

keys_a = sorted(aspect_stats)
axes[1].bar([aspect_labels[k] for k in keys_a], [aspect_stats[k][0] for k in keys_a], color=["#1a9850", "#fdae61", "#d73027"])
axes[1].set_title("Baki -> Ortalama dNBR\n(Temiz Maske)")

keys_n = sorted(ndvi_stats)
axes[2].bar([severity_labels.get(k, k) for k in keys_n], [ndvi_stats[k][0] for k in keys_n],
            color=["#4d4d4d", "#1a9850", "#fee08b", "#fdae61", "#d73027"][: len(keys_n)])
axes[2].set_title("Siddet -> Ortalama Yangin-Oncesi NDVI\n(Temiz Maske)")

fig.suptitle("Dogrulamalarin Tekrari: Sadece Gercek Yangin Lekesi (Siniflandirma Gurultusu Cikarilmis)", fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_dogrulama_temiz_maske.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()
print(f"Kaydedildi: {out_png}")

# Gecici UTM dosyalarini temizle
arcpy.management.Delete(slope_utm)
arcpy.management.Delete(aspect_utm)
arcpy.CheckInExtension("Spatial")
print("\n!!! TAMAMLANDI !!!")
