import arcpy
import os

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
arcpy.env.workspace = workspace

files_to_check = [
    "dNBR_Full_Masked_Classified.tif",
    "Recovery_NBR_2022.tif",
    "Recovery_NBR_2024.tif",
    "Manavgat_Slope.tif",
    "Future_Fire_Risk.tif"
]

print("--- GIS Veri Kalite Kontrolu (QC) ---")
for f in files_to_check:
    path = os.path.join(workspace, f)
    if os.path.exists(path):
        raster = arcpy.Raster(path)
        desc = arcpy.Describe(raster)
        
        # Ozet istatistikler
        arcpy.management.CalculateStatistics(path)
        min_val = raster.minimum
        max_val = raster.maximum
        
        print(f"\nDosya: {f}")
        print(f" - CRS (Projeksiyon): {desc.spatialReference.name}")
        print(f" - Cozunurluk (Hucre Boyutu): {desc.meanCellWidth:.2f} x {desc.meanCellHeight:.2f}")
        print(f" - Min Deger: {min_val:.2f}, Max Deger: {max_val:.2f}")
        
        if desc.spatialReference.name == "Unknown":
            print("   [HATA] Projeksiyon eksik!")
        else:
            print("   [BASARILI] Projeksiyon gecerli.")
            
        if min_val == max_val:
            print("   [UYARI] Butun pikseller ayni degere sahip olabilir (Bos veri?).")
        else:
            print("   [BASARILI] Veri dagilimi normal.")
    else:
        print(f"\n[HATA] {f} bulunamadi!")
print("\n--- QC Tamamlandi ---")
