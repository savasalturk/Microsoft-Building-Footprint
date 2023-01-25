import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
import geopandas as gpd
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = 'postgresql://username:password@localhost:5432/database'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)


gdf = gpd.read_postgis(
    "SELECT * FROM microsoftbuildingfootprint;", con=engine, geom_col="geom")


iller = gpd.read_file("data\gadm40_TUR_1.shp")
iller = iller.to_crs(4326)


s_poly = gdf.values
del gdf


fig, ax = plt.subplots(figsize=(16, 9), subplot_kw=dict(aspect='equal'))


iller.plot(ax=ax, color="red", alpha=0.08, edgecolor="black")
del iller


def plot_polygon(arraygeom, **kwargs):
    patches = []
    for _,poly in arraygeom:
        path = Path.make_compound_path(
            Path(np.asarray(poly.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

        patch = PathPatch(path, **kwargs)
        patches.append(patch)
    return patches


patches = plot_polygon(s_poly, facecolor='red', edgecolor='red')


collection = PatchCollection(
    patches, facecolor="red", edgecolor="red", linewidth=0.05)


ax.add_collection(collection, autolim=True)
ax.autoscale_view()
plt.axis("off")
plt.tight_layout()
plt.savefig(r"img\vis.png", dpi=150)
plt.close()
