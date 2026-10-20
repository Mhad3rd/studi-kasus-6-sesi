"""Sesi 6 - Visualisasi data: hapus chartjunk & terapkan mantra 'Overview first, zoom & filter, details on demand'."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(11)
wilayah = ["Sumatra", "Jawa", "Kalimantan", "Sulawesi", "Papua"]
basis = dict(zip(wilayah, [80, 150, 60, 55, 30]))
bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
data = pd.DataFrame({w: (b * (1 + .25 * np.sin(np.arange(12) / 12 * 2 * np.pi)) + rng.normal(0, 5, 12)).round(1)
                     for w, b in basis.items()}, index=bulan)
total = data.sum().sort_values()

# 1) Sebelum vs sesudah (chartjunk -> bersih)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].pie(total.values, labels=total.index, explode=[.1] * 5, shadow=True,
          colors=plt.cm.gist_rainbow(np.linspace(0, 1, 5)), autopct="%1.2f%%")
ax[0].set_title("SEBELUM: pie + shadow + warna pelangi", color="#C44E52")
warna = ["#bbbbbb"] * 4 + ["#4C72B0"]
ax[1].barh(total.index, total.values, color=warna)
for i, v in enumerate(total.values): ax[1].text(v + 5, i, f"{v:,.0f}", va="center")
for s in ["top", "right", "bottom"]: ax[1].spines[s].set_visible(False)
ax[1].set_xticks([]); ax[1].set_title("SESUDAH: bar terurut, 1 warna sorotan, label langsung", color="#2a7")
plt.tight_layout(); plt.savefig("sesi6_visualisasi_data/sebelum_sesudah.png", dpi=130); plt.close()

# 2) Overview -> Zoom & Filter -> Details on demand
def filter_wilayah(nama): return data[nama]
top = total.index[-1]; seri = filter_wilayah(top); puncak = seri.idxmax()
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ax[0].bar(total.index, total.values, color=["#ccc"] * 4 + ["#4C72B0"]); ax[0].set_title("1. OVERVIEW: total per wilayah"); ax[0].tick_params(axis="x", rotation=30)
for w in wilayah: ax[1].plot(bulan, data[w], color="#ddd", lw=1)
ax[1].plot(bulan, seri, color="#4C72B0", lw=2.5, marker="o"); ax[1].set_title(f"2. ZOOM & FILTER: {top}"); ax[1].tick_params(axis="x", rotation=45)
ax[2].plot(bulan, seri, color="#4C72B0", lw=2); ax[2].annotate(f"Puncak: {puncak}\n{seri.max():.1f} unit", (puncak, seri.max()),
          xytext=(0, -45), textcoords="offset points", arrowprops=dict(arrowstyle="->"), ha="center", weight="bold")
ax[2].set_title("3. DETAIL ON DEMAND"); ax[2].tick_params(axis="x", rotation=45)
for a in ax: a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("sesi6_visualisasi_data/overview_zoom_detail.png", dpi=130)
print("Total per wilayah:\n", total.round(0).to_string())
print(f"\nFilter '{top}' -> puncak penjualan di {puncak} = {seri.max():.1f} unit, rata-rata {seri.mean():.1f}")
