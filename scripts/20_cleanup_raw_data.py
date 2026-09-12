import os

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"

# Sadece bu dosyalar ve bunlara bagli .xml, .ovr gibi ek dosyalar korunacak
keep_files = [
    "pre_tci_mosaic.tif",
    "post_tci_mosaic.mosaic.tif", # Wait, it's post_tci_mosaic.tif
    "dNBR_Full_Masked_Classified.tif",
    "Recovery_Full_NBR_2022.tif",
    "Recovery_Full_NBR_2023.tif",
    "Recovery_Full_NBR_2024.tif",
    "burn_colors.clr"
]

# Fixed typo in keep_files
keep_files[1] = "post_tci_mosaic.tif"

all_files = os.listdir(workspace)

deleted_count = 0
for f in all_files:
    should_keep = False
    for kf in keep_files:
        if f.startswith(kf):
            should_keep = True
            break
            
    if not should_keep:
        try:
            os.remove(os.path.join(workspace, f))
            deleted_count += 1
        except Exception as e:
            pass # Cogu dosya silinecek, kilitli olanlar silinemeyebilir

print(f"Temizlik tamamlandi! {deleted_count} gereksiz ve hatali dosya silindi.")
