import arcpy
from arcpy.sa import *
import os

print("🔥 Adım 2: Su Maskeleme ve Sınıflandırma Başlıyor 🔥")

# Workspace and inputs
workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

pre_b8 = os.path.join(workspace, "pre_fire_B08.tif")
pre_b12 = os.path.join(workspace, "pre_fire_B12.tif")
post_b8 = os.path.join(workspace, "post_fire_B08.tif")
post_b12 = os.path.join(workspace, "post_fire_B12.tif")
pre_scl = os.path.join(workspace, "pre_fire_SCL.tif")
post_scl = os.path.join(workspace, "post_fire_SCL.tif")

print("1. Rasterlar ve SCL katmanları yükleniyor...")
# To match resolutions, we set the environment cell size and snap raster to B08 (10m)
arcpy.env.cellSize = pre_b8
arcpy.env.snapRaster = pre_b8

# Load as Raster objects
r_pre_b8 = Raster(pre_b8)
r_pre_b12 = Raster(pre_b12)
r_post_b8 = Raster(post_b8)
r_post_b12 = Raster(post_b12)
r_pre_scl = Raster(pre_scl)
r_post_scl = Raster(post_scl)

print("2. Maskeleme Kuralları Uygulanıyor (Su, Bulut, Gölge siliniyor)...")
# SCL values: 6=Water, 3=Cloud Shadow, 8/9/10=Clouds, 11=Snow
def get_valid_mask(scl_raster):
    # Create boolean raster: 1 if valid, 0 if invalid (water/cloud)
    return Con((scl_raster == 6) | (scl_raster == 3) | (scl_raster == 8) | (scl_raster == 9) | (scl_raster == 10) | (scl_raster == 11), 0, 1)

pre_valid = get_valid_mask(r_pre_scl)
post_valid = get_valid_mask(r_post_scl)
final_valid_mask = pre_valid & post_valid

print("3. dNBR Hesaplanıyor...")
pre_nbr = (Float(r_pre_b8) - Float(r_pre_b12)) / (Float(r_pre_b8) + Float(r_pre_b12))
post_nbr = (Float(r_post_b8) - Float(r_post_b12)) / (Float(r_post_b8) + Float(r_post_b12))
dnbr = pre_nbr - post_nbr

print("4. Maske dNBR üzerine uygulanıyor...")
# SetNull: If condition is true (mask==0), set to Null, else keep dNBR
dnbr_masked = SetNull(final_valid_mask == 0, dnbr)

print("5. Sınıflandırma (USGS Burn Severity) Yapılıyor...")
remap = RemapRange([
    [-5.0, 0.1, 1],   
    [0.1, 0.27, 2],   
    [0.27, 0.44, 3],  
    [0.44, 0.66, 4],  
    [0.66, 5.0, 5]    
])
out_reclass = Reclassify(dnbr_masked, "Value", remap)

out_file = os.path.join(workspace, "dNBR_Masked_Classified.tif")
out_reclass.save(out_file)

print(f"✅ İşlem tamam! Maskelenmiş ve sınıflandırılmış dosya: {out_file}")
print("Bu dosyayı ArcGIS Pro'ya sürükleyip 1. sınıfı 'No Color' yaparsanız, tüm göllerin temizlendiğini göreceksiniz!")
