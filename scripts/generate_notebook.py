import nbformat as nbf
import os

print("Esri Portfolyosu icin Jupyter Notebook olusturuluyor...")

nb = nbf.v4.new_notebook()

text_1 = """# Wildfire Damage & Drought Impact Analysis using ArcGIS
## Manavgat, Turkey (2021)

This notebook demonstrates an advanced spatial data science workflow using the **ArcGIS API for Python** (`arcgis`), **ArcPy**, and **ArcGIS Pro** to assess the severe wildfire that occurred in Manavgat, Turkey in July 2021.

### 🌟 Project Highlights:
- **Scientific Accuracy:** True 16-bit Sentinel-2 L2A imagery processing via `arcpy` Raster Functions.
- **Burn Severity Mapping:** Normalized Burn Ratio (dNBR) modeling.
- **Drought & Recovery Tracking:** Normalized Difference Moisture Index (NDMI) time-series analysis (2021 - 2023).
- **3D Spatial Visualization:** Local Scene modeling with DEM integration.

---"""

code_1 = """# Import ArcGIS API for Python
from arcgis.gis import GIS
from arcgis.raster.functions import *
import warnings
warnings.filterwarnings('ignore')

print("ArcGIS kütüphaneleri başarıyla yüklendi. Bağlantı kuruluyor...")
# Anonymous connection to ArcGIS Online (or use your credentials)
gis = GIS()
print("Bağlı olunan portal:", gis.url)"""

text_2 = """### 1. Interactive Web Map: Wildfire Location
Let's initialize an interactive map focused on the Manavgat region."""

code_2 = """# Create an interactive map widget
m = gis.map("Manavgat, Antalya, Turkey", zoomlevel=10)
m.basemap = "satellite"
m"""

text_3 = """### 2. Meteorological Context (Why did it spread so fast?)
Using open weather data, we tracked the extreme conditions during the fire ignition.
- **Temperature:** Reached ~40°C
- **Wind Speed:** Exceeded 45 km/h

*(See the generated `manavgat_yangin_meteorolojisi.png` in the repository).*"""

text_4 = """### 3. Burn Severity & Moisture Recovery (ArcPy Workflow)
The heavy lifting (pixel-perfect Raster Math) was automated using **ArcPy** within ArcGIS Pro.
By utilizing true 16-bit Sentinel-2 bands (Band 8 - NIR, Band 12 - SWIR2), we generated scientific dNBR and NDMI models.

```python
# Snippet of the ArcPy automation used in ArcGIS Pro:
import arcpy
from arcpy.sa import *

arcpy.env.workspace = r"C:\Data\Sentinel2"
nir = Raster("B08_10m.tif")
swir = Raster("B12_20m.tif")

# Calculate NDMI (Moisture Index)
ndmi = (nir - swir) / (nir + swir)
ndmi.save("NDMI_Result.tif")
```
*(The full `arcpy_scientific_analysis.py` script is available in this repository).*"""

text_5 = """### 4. 3D Scene Visualization
Using ArcGIS Pro's Local Scene, the resulting dNBR layer was draped over a high-resolution DEM. This allowed us to visualize the fire's path across the Taurus Mountains' rugged topography. 

Please check the **`3D_Flythrough.mp4`** video attached to the repository for the animated fly-through!"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text_1),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_markdown_cell(text_2),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_markdown_cell(text_3),
    nbf.v4.new_markdown_cell(text_4),
    nbf.v4.new_markdown_cell(text_5)
]

output_file = "Wildfire_Analysis_with_ArcGIS.ipynb"
with open(output_file, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"✅ {output_file} basariyla uretildi!")
