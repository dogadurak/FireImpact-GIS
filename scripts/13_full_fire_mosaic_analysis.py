import arcpy
from arcpy.sa import *
import os

print("🔥 Adım 4: Tüm Yangın Alanı Birleştiriliyor (Mosaic) ve Sınıflandırılıyor 🔥")

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

print("1. Kuzey (T36SUG) ve Güney (T36SUF) kareleri birleştiriliyor (Mosaic)...")

def mosaic_rasters(raster_list, out_name):
    print(f"Birleştiriliyor: {out_name}...")
    arcpy.management.MosaicToNewRaster(
        input_rasters=raster_list,
        output_location=workspace,
        raster_dataset_name_with_extension=out_name,
        pixel_type="16_BIT_UNSIGNED",
        number_of_bands=1,
        mosaic_method="LAST"
    )
    return os.path.join(workspace, out_name)

# B08 and B12 Pre
pre_b8_mosaic = mosaic_rasters(["pre_fire_B08.tif", "pre_fire_south_B08.tif"], "pre_b8_mosaic.tif")
pre_b12_mosaic = mosaic_rasters(["pre_fire_B12.tif", "pre_fire_south_B12.tif"], "pre_b12_mosaic.tif")
pre_scl_mosaic = mosaic_rasters(["pre_fire_SCL.tif", "pre_fire_south_SCL.tif"], "pre_scl_mosaic.tif")

# B08 and B12 Post
post_b8_mosaic = mosaic_rasters(["post_fire_B08.tif", "post_fire_south_B08.tif"], "post_b8_mosaic.tif")
post_b12_mosaic = mosaic_rasters(["post_fire_B12.tif", "post_fire_south_B12.tif"], "post_b12_mosaic.tif")
post_scl_mosaic = mosaic_rasters(["post_fire_SCL.tif", "post_fire_south_SCL.tif"], "post_scl_mosaic.tif")

print("2. Devasa haritalar (200km x 100km) yükleniyor...")
arcpy.env.cellSize = pre_b8_mosaic
arcpy.env.snapRaster = pre_b8_mosaic

r_pre_b8 = Raster(pre_b8_mosaic)
r_pre_b12 = Raster(pre_b12_mosaic)
r_post_b8 = Raster(post_b8_mosaic)
r_post_b12 = Raster(post_b12_mosaic)
r_pre_scl = Raster(pre_scl_mosaic)
r_post_scl = Raster(post_scl_mosaic)

print("3. Maskeleme Kuralları Uygulanıyor (Su, Bulut, Gölge siliniyor)...")
def get_valid_mask(scl_raster):
    return Con((scl_raster == 6) | (scl_raster == 3) | (scl_raster == 8) | (scl_raster == 9) | (scl_raster == 10) | (scl_raster == 11), 0, 1)

pre_valid = get_valid_mask(r_pre_scl)
post_valid = get_valid_mask(r_post_scl)
final_valid_mask = pre_valid & post_valid

print("4. dNBR Hesaplanıyor...")
pre_nbr = (Float(r_pre_b8) - Float(r_pre_b12)) / (Float(r_pre_b8) + Float(r_pre_b12))
post_nbr = (Float(r_post_b8) - Float(r_post_b12)) / (Float(r_post_b8) + Float(r_post_b12))
dnbr = pre_nbr - post_nbr
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
out_file = os.path.join(workspace, "dNBR_Full_Masked_Classified.tif")

print("Sonuç kaydediliyor (Bu işlem devasa boyut nedeniyle 15-20 dk sürebilir)...")
out_reclass.save(out_file)

# Release locks
del out_reclass
del dnbr_masked
del final_valid_mask

print("6. Renklendirme dosyası oluşturuluyor...")
clr_file = os.path.join(workspace, "burn_colors.clr")
with open(clr_file, "w") as f:
    f.write("1 255 255 255\n")
    f.write("2 255 255 0\n")
    f.write("3 255 170 0\n")
    f.write("4 255 0 0\n")
    f.write("5 115 0 0\n")

print("7. Haritaya ekleniyor...")
try:
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    map_obj = aprx.listMaps()[0]
    map_obj.addDataFromPath(out_file)
except:
    pass

print(f"✅ BÜTÜN İŞLEMLER TAMAMLANDI! {out_file}")
print("NOT: Hata almamak için renklendirmeyi (Sarı-Kırmızı) manuel olarak yapabilirsiniz.")
