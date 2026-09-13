import os
import arcpy
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt

# DOGRU YONTEMLE ARAZI HESABI + RISK MODELI V4
#
# scripts/17 ve 25, Egim/Baki'yi DEM COGRAFI (derece bazli, GCS_WGS_1984)
# koordinat sistemindeyken hesaplamis, SONRA sonucu UTM'e projeksiyonlamisti.
# Dogrusu: ONCE DEM'i projeksiyonlamak (metre bazli), SONRA egim/baki'yi
# DOGRUDAN projeksiyonlu DEM'den hesaplamaktir.
#
# Bu script dogru sirayla yeniden hesaplar ve V3'u (Baki + NDVI) bu duzeltilmis
# Baki ile V4 olarak yeniden uretir. Not: Eslestirme testi (bkz. konusma),
# iki yontem arasinda sonuclarin pratikte hemen hemen ayni ciktigini gostermisti
# (Egim: Duz 0.379->0.372, Orta 0.433->0.443, Dik 0.395->0.398) -- yani bu bir
# "hata duzeltmesi" degil, metodolojik titizlik/dogrulama adimidir.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

utm36n = arcpy.SpatialReference(32636)

print("1. DEM once UTM 36N'e projeksiyonlandiriliyor (kalici, dogru sira icin)...")
dem_utm = os.path.join(workspace, "Manavgat_DEM_UTM.tif")
arcpy.management.ProjectRaster(os.path.join(workspace, "Manavgat_DEM.tif"), dem_utm, utm36n, "BILINEAR", 20)

print("2. Egim ve Baki, DOGRUDAN projeksiyonlu DEM'den hesaplaniyor...")
slope_correct = Slope(Raster(dem_utm), "DEGREE")
slope_correct.save(os.path.join(workspace, "Manavgat_Slope_Correct.tif"))
aspect_correct = Aspect(Raster(dem_utm))
aspect_correct.save(os.path.join(workspace, "Manavgat_Aspect_Correct.tif"))

print("3. NDVI (fuel yuku, scripts/25'ten zaten mevcut) ile birlestiriliyor...")
ndvi_full_path = os.path.join(workspace, "Pre_Fire_NDVI_Full.tif")
arcpy.env.extent = arcpy.Describe(ndvi_full_path).extent
arcpy.env.cellSize = 20
arcpy.env.snapRaster = ndvi_full_path

aspect_reclass = Reclassify(aspect_correct, "Value",
                            RemapRange([[-1, 90, 1], [90, 135, 2], [135, 225, 3], [225, 270, 2], [270, 360, 1]]))
ndvi_reclass = Reclassify(Raster(ndvi_full_path), "Value", RemapRange([[-1.0, 0.3, 1], [0.3, 0.5, 2], [0.5, 1.0, 3]]))

arcpy.env.extent = "MINOF"
risk_model = (aspect_reclass * 0.5) + (ndvi_reclass * 0.5)
risk_model_int = Int(risk_model + 0.5)
risk_out = os.path.join(workspace, "Future_Fire_Risk_V4.tif")
risk_model_int.save(risk_out)
print(f"   Kaydedildi: {risk_out}")

print("4. V3 ile V4 arasindaki fark kontrol ediliyor (dogrulama)...")
v3_path = os.path.join(workspace, "Future_Fire_Risk_V3.tif")
arcpy.env.extent = "MINOF"
diff = Raster(v3_path) - risk_model_int
diff_arr = arcpy.RasterToNumPyArray(diff, nodata_to_value=-999)
valid = diff_arr != -999
total_px = valid.sum()
same_px = (diff_arr[valid] == 0).sum()
print(f"   V3 ve V4 ayni siniftaki piksel orani: {same_px/total_px*100:.2f}% ({same_px:,}/{total_px:,})")

print("5. PNG onizleme uretiliyor...")
arr_raw = arcpy.RasterToNumPyArray(risk_model_int, nodata_to_value=255)
arr = arr_raw.astype(float)
arr[arr == 255] = np.nan
plt.figure(figsize=(10, 6))
plt.imshow(arr, cmap="RdYlGn_r")
plt.colorbar(label="Risk Seviyesi (1: Dusuk, 3: Yuksek)")
plt.title("Gelecek Yangin Riski Modeli V4 (Duzeltilmis Baki + Yakit Yuku/NDVI)")
plt.axis("off")
out_png = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\manavgat_gelecek_yangin_riski_v3.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n!!! TAMAMLANDI !!! Risk haritasi (V4): {risk_out}")
arcpy.management.Delete(dem_utm)
arcpy.CheckInExtension("Spatial")
