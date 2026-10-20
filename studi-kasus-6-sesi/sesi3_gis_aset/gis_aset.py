"""Sesi 3 - GIS & Asset Management: penugasan lampu jalan rusak ke depot terdekat (Haversine),
penentuan prioritas, dan ekspor GeoJSON yang bisa dibuka di QGIS/ArcGIS."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

rng = np.random.default_rng(7)
depot = pd.DataFrame({"depot": ["Utara", "Selatan", "Timur"], "lat": [-6.86, -6.95, -6.91], "lon": [107.60, 107.60, 107.67]})
n = 60
aset = pd.DataFrame({"id": [f"LJ-{i:03d}" for i in range(1, n + 1)],
                     "lat": rng.uniform(-6.97, -6.84, n), "lon": rng.uniform(107.55, 107.70, n),
                     "kerusakan": rng.integers(1, 4, n)})
D = np.stack([haversine(aset.lat.values, aset.lon.values, d.lat, d.lon) for d in depot.itertuples()], axis=1)
aset["depot"] = depot.depot.values[D.argmin(1)]
aset["jarak_km"] = D.min(1)
aset["prioritas"] = aset.kerusakan * 10 - aset.jarak_km

print("=== Ringkasan per depot ===")
print(aset.groupby("depot").agg(jumlah=("id", "count"), rata_jarak_km=("jarak_km", "mean"),
                                 total_km=("jarak_km", "sum")).round(2).to_string())
print(f"\nJarak total jika SEMUA dari depot Utara : {D[:, 0].sum():.1f} km")
print(f"Jarak total dengan depot terdekat       : {D.min(1).sum():.1f} km")
print("\n=== 5 aset prioritas utama ===")
print(aset.sort_values("prioritas", ascending=False).head(5)[["id", "depot", "kerusakan", "jarak_km"]].round(2).to_string(index=False))

geo = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [r.lon, r.lat]},
     "properties": {"id": r.id, "kerusakan": int(r.kerusakan), "depot": r.depot, "jarak_km": round(r.jarak_km, 3)}}
    for r in aset.itertuples()]}
json.dump(geo, open("sesi3_gis_aset/aset.geojson", "w"), indent=1)

warna = {"Utara": "#4C72B0", "Selatan": "#55A868", "Timur": "#C44E52"}
fig, ax = plt.subplots(figsize=(7, 6))
for r in aset.itertuples():
    d = depot[depot.depot == r.depot].iloc[0]
    ax.plot([r.lon, d.lon], [r.lat, d.lat], color=warna[r.depot], alpha=.2, lw=.8)
    ax.scatter(r.lon, r.lat, s=r.kerusakan * 35, color=warna[r.depot], edgecolor="white", zorder=3)
for d in depot.itertuples():
    ax.scatter(d.lon, d.lat, marker="*", s=400, color=warna[d.depot], edgecolor="black", zorder=4)
    ax.annotate(d.depot, (d.lon, d.lat), xytext=(6, 6), textcoords="offset points", weight="bold")
ax.set_title("Penugasan aset ke depot terdekat\n(ukuran titik = tingkat kerusakan)")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); plt.tight_layout()
plt.savefig("sesi3_gis_aset/hasil.png", dpi=130)
