from PIL import Image
import os

print("NDMI zaman serisi icin canli demo GIF (Video) olusturuluyor...")

# Dosya yollari
image_files = [
    "manavgat_ndmi_2021_map.png",
    "manavgat_ndmi_2022_map.png",
    "manavgat_ndmi_2023_map.png"
]

images = []
for file in image_files:
    if os.path.exists(file):
        images.append(Image.open(file))
    else:
        print(f"Hata: {file} bulunamadi!")

if len(images) == 3:
    # GIF olarak kaydet
    out_gif = "manavgat_kuraklik_iyilesme_demo.gif"
    
    # Ilk resmi baz alarak digerlerini de ekle, her kare arasinda 1.5 saniye (1500 ms) bosluk birak
    images[0].save(
        out_gif,
        save_all=True,
        append_images=images[1:],
        duration=1500,
        loop=0  # Sonsuz dongu
    )
    print(f"✅ Harika! Canli demo GIF uretildi: {out_gif}")
    print("Bu GIF'i StoryMaps'te 'Resim' olarak eklediginizde hareketli video gibi oynayacaktir.")
else:
    print("Tum resimler bulunamadigi icin GIF olusturulamadi.")
