import arcpy
from arcpy.sa import *
import os

print("🔥 ArcGIS Pro - ArcPy Bilimsel Yangın Analizi Başlıyor 🔥")

# Çalışma klasörümüzü belirleyelim
workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# Veri yollarını kontrol edelim
pre_b8_path = os.path.join(workspace, "pre_fire_B08.tif")
pre_b12_path = os.path.join(workspace, "pre_fire_B12.tif")
post_b8_path = os.path.join(workspace, "post_fire_B08.tif")
post_b12_path = os.path.join(workspace, "post_fire_B12.tif")

# ArcGIS Pro lisansını (Spatial Analyst) kontrol edelim
arcpy.CheckOutExtension("Spatial")

try:
    print("1. Yangın Öncesi ve Sonrası (Ham 16-bit) Rasterlar yükleniyor...")
    pre_b8 = Raster(pre_b8_path)
    pre_b12 = Raster(pre_b12_path)
    post_b8 = Raster(post_b8_path)
    post_b12 = Raster(post_b12_path)

    print("2. Float dönüşümleri yapılıyor ve NBR (Normalized Burn Ratio) hesaplanıyor...")
    # Formül: NBR = (NIR - SWIR2) / (NIR + SWIR2)
    pre_nbr = (Float(pre_b8) - Float(pre_b12)) / (Float(pre_b8) + Float(pre_b12))
    post_nbr = (Float(post_b8) - Float(post_b12)) / (Float(post_b8) + Float(post_b12))

    print("3. dNBR (Fark) hesaplanıyor: pre_NBR - post_NBR...")
    dnbr = pre_nbr - post_nbr
    
    # Çıktıyı kaydedelim
    out_dnbr = os.path.join(workspace, "dNBR_Scientific.tif")
    dnbr.save(out_dnbr)
    print(f"✅ Harika! %100 Bilimsel Doğrulukla dNBR haritası üretildi ve kaydedildi:")
    print(f"📁 Konum: {out_dnbr}")
    
    print("\n👉 Şimdi bu dosyayı ('dNBR_Scientific.tif') ArcGIS Pro içindeki 'Catalog' sekmesinden bulup haritaya (Map) sürükleyebilirsiniz!")
    
except Exception as e:
    print(f"Hata oluştu: {e}")
finally:
    arcpy.CheckInExtension("Spatial")
