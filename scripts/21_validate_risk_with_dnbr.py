import arcpy
from arcpy.sa import *
import os
import matplotlib.pyplot as plt

# Bu script, Future_Fire_Risk modelinin temel varsayimini (dik + guney bakili
# yamaclar daha siddetli yanar) 2021'in gercek dNBR verisiyle test eder.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

dnbr_mask_path = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")
dnbr_scientific_path = os.path.join(workspace, "dNBR_Scientific.tif")
slope_path = os.path.join(workspace, "Manavgat_Slope.tif")
aspect_path = os.path.join(workspace, "Manavgat_Aspect.tif")

utm36n = arcpy.SpatialReference(32636)  # WGS 1984 UTM Zone 36N (dNBR ile ayni)

print("1. Egim/Baki, dNBR ile karsilastirmak icin UTM 36N'e projeksiyonlandiriliyor...")
slope_utm = os.path.join(workspace, "Manavgat_Slope_UTM.tif")
aspect_utm = os.path.join(workspace, "Manavgat_Aspect_UTM.tif")
arcpy.management.ProjectRaster(slope_path, slope_utm, utm36n, "BILINEAR", 20)
arcpy.management.ProjectRaster(aspect_path, aspect_utm, utm36n, "NEAREST", 20)

print("2. Egim ve baki, risk modeliyle ayni esiklere gore siniflandiriliyor...")
slope_reclass = Reclassify(Raster(slope_utm), "Value", RemapRange([[0, 15, 1], [15, 30, 2], [30, 90, 3]]))
aspect_reclass = Reclassify(Raster(aspect_utm), "Value",
                             RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))

print("3. Sadece 2021'de gercekten yanan alanla maskeleniyor...")
slope_masked = ExtractByMask(slope_reclass, dnbr_mask_path)
aspect_masked = ExtractByMask(aspect_reclass, dnbr_mask_path)

print("4. Zonal Statistics: her sinif icin ortalama gercek dNBR degeri hesaplaniyor...")
slope_table = os.path.join(workspace, "zonal_dnbr_by_slope.dbf")
aspect_table = os.path.join(workspace, "zonal_dnbr_by_aspect.dbf")
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

slope_labels = {1: "Duz / Az Egimli\n(0-15 derece)", 2: "Orta Egimli\n(15-30 derece)", 3: "Dik\n(>30 derece)"}
aspect_labels = {1: "Kuzey Baki\n(Serin/Nemli)", 2: "Dogu/Bati Baki\n(Orta)", 3: "Guney Baki\n(Sicak/Kuru)"}

print("\n--- SONUCLAR: Egim Sinifina Gore Ortalama Gercek dNBR ---")
for k in sorted(slope_stats):
    mean, count = slope_stats[k]
    print(f"  {slope_labels.get(k, k)}: ortalama dNBR = {mean:.4f}  (piksel sayisi: {count})")

print("\n--- SONUCLAR: Baki Sinifina Gore Ortalama Gercek dNBR ---")
for k in sorted(aspect_stats):
    mean, count = aspect_stats[k]
    print(f"  {aspect_labels.get(k, k)}: ortalama dNBR = {mean:.4f}  (piksel sayisi: {count})")

print("\n5. Dogrulama grafigi olusturuluyor...")
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

keys_s = sorted(slope_stats)
axes[0].bar([slope_labels[k] for k in keys_s], [slope_stats[k][0] for k in keys_s], color=["#1a9850", "#fdae61", "#d73027"])
axes[0].set_title("Egim Sinifina Gore\nOrtalama Yanma Siddeti (dNBR)")
axes[0].set_ylabel("Ortalama dNBR")

keys_a = sorted(aspect_stats)
axes[1].bar([aspect_labels[k] for k in keys_a], [aspect_stats[k][0] for k in keys_a], color=["#1a9850", "#fdae61", "#d73027"])
axes[1].set_title("Baki Sinifina Gore\nOrtalama Yanma Siddeti (dNBR)")
axes[1].set_ylabel("Ortalama dNBR")

fig.suptitle("Risk Modeli Dogrulamasi: Topografya Gercekten Yanma Siddetini Aciklyor mu?", fontsize=13, fontweight="bold")
fig.tight_layout()
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_risk_model_dogrulama.png"
fig.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Dogrulama grafigi kaydedildi: {out_png}")
arcpy.CheckInExtension("Spatial")
