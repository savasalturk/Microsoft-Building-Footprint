# Building Footprint - Turkey

Açık verinin önemi gün geçtikçe daha da önem kazanıyor. 2022 yılında Microsoft bina ayak izlerinin olduğu verileri paylaştı.
Microsoftun açık veri olarak yayınladığı bina ayak izi verilerine [buradan](https://github.com/microsoft/GlobalMLBuildingFootprints) ulaşabilirsiniz. 

>  **Not-1:** Github sayfasında ekim ayında güncelleme yapılmış. Daha önceki veriler ülkelere ve bölgelere göre linkleri ayrı olarak eklenmişti. Ben ekim ayı öncesindeki verileri indirmiştim. Dosya geojson formatında ve 5.5 GB boyutundaydı. Detaylı incelemek isterseniz paylaştığım github sayfasına bakabilirsiniz.

>  **Not-2:** Bu veride hatalı veya eksik bina ayak izi olabilir.


## Aşama 1
İndirilen geojson formatındaki dosya PostGIS'i kurduğum PostgreSQL veritabanına aktardım. 

Gerekli paketler eklendi.

```python
import json
import psycopg2
```

Veritabanına bağlanmak için:

```python
def connect(host="localhost", database="", user="", password=""):
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password)
    conn.autocommit = True
    cur = conn.cursor()
    return cur

cur = connect()
```
Aşağıdaki işlem ile dosyayı okuyup veritabanında oluşturduğum tabloya verileri ekliyor.
```python
file = open(r"data\Turkey.geojsonl","r").readlines()
sql = """INSERT INTO microsoftbuildingfootprint(geom) values(st_astext(ST_GeomFromGeoJSON('{}')))"""
for i in file:
    sql_send = sql.format(json.dumps(json.loads(i)["geometry"]))
    cur.execute(sql_send)
```

Ayrıca sql sorgularının hızlanmasi için index oluşturmak gerekli. Go ve Python ile uygulamalar yaptım. Fırsat bulursam bununla alakalı bir paylaşım yapmayı düşünüyorum :) 
```sql
CREATE INDEX microsoftbuildingfootprint_geom_idx
  ON microsoftbuildingfootprint
  USING GIST (geom);
```

### **Genel bilgiler:**
- Toplam 18,064,082 polygon 
- İstanbul: 827,478 polygon
- Ankara: 707,869 polygon
- İzmir: 916,122 polygon
- Van: 211,634 polygon
- İstanbul:
    - ![ornekalan](./img/istanbul.JPG)

- Beşiktaş, Şişli:
    - ![ornekalan](./img/besiktassisli.JPG)
- Van:
    - ![ornekalan](./img/van.JPG)
- Bazı bölgelerde veri eksik.
    - ![Görsel](./img/eksik1.JPG)
    - ![Görsel](./img/eksik2.JPG)


## Aşama 2


Gerekli kütüphaneler aktarıldı.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import geopandas as gpd
from sqlalchemy import create_engine
```
Veritabanına bağlanmak için:
```python
SQLALCHEMY_DATABASE_URL = 'postgresql://username:password@localhost:5432/database'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
``` 

Geopandas ile veriler okundu. 
```python 
gdf = gpd.read_postgis(
    "SELECT * FROM microsoftbuildingfootprint;", con=engine, geom_col="geom")
```

Türkiye il sınırlarının olduğu veriye [buradan](https://gadm.org/download_country.html) ulaşabilirsiniz.

```python 
iller = gpd.read_file("D:\PROJECTS\PlanAskiVeriler\il\gadm40_TUR_1.shp")
# 4326 koordinat sistemine dönüştürüldü.
iller = iller.to_crs(4326)
```
Performansı arttırmak için numpy dizisine çevrildi.

```python
s_poly = gdf.values
# veri büyük olduğu için bellekten siliyoruz
del gdf
```
Figure oluşturuldu.

```python
fig, ax = plt.subplots(figsize=(16, 9), subplot_kw=dict(aspect='equal'))

```
Türkiye il sınırlarının olduğu polygon çizdirildi.
```python
iller.plot(ax=ax, color="red", alpha=0.08, edgecolor="black")
# bellekten kaldırıldı.
del iller
```
Binaları çizdirmek için fonksiyon tanımlandı. gdf.plot() yavaş çalıştığı için bu yöntem uygulandı.


```python
def plot_polygon(arraygeom, **kwargs):
    patches = []
    for _,poly in arraygeom:
        path = Path.make_compound_path(
            Path(np.asarray(poly.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

        patch = PathPatch(path, **kwargs)
        patches.append(patch)
    return patches
```


Tanımlanan fonksiyon çalıştırıldı. 

```python
patches = plot_polygon(s_poly, facecolor='red', edgecolor='red')


collection = PatchCollection(
    patches, facecolor="red", edgecolor="red", linewidth=0.05)


ax.add_collection(collection, autolim=True)
ax.autoscale_view()
plt.axis("off")
plt.tight_layout()
plt.savefig(r"img\vis.png", dpi=150)
plt.close()
```

# Görsel



![Görsel](./img/vis.png)