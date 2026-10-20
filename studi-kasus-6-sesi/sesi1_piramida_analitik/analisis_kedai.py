"""Sesi 1 - Piramida Analitik: Data -> Informasi -> Insight -> Keputusan.
Studi kasus: penjualan kopi sebuah UMKM (data sintetis, sengaja dibuat 'kotor')."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(42)
N = 180
tgl = pd.date_range("2025-01-01", periods=N)
promo = (rng.random(N) < 0.25).astype(int)
weekend = (tgl.dayofweek >= 5).astype(int)
jual = 100 + 25 * weekend + 30 * promo + 0.15 * np.arange(N) + rng.normal(0, 8, N)
df = pd.DataFrame({"tanggal": tgl, "cangkir": jual.round(), "promo": promo, "akhir_pekan": weekend})
df.loc[[10, 45, 90], "cangkir"] = np.nan   # data kosong
df.loc[20, "cangkir"] = -50                # salah input
df.loc[120, "cangkir"] = 5000              # outlier

print("=== 0. DATA PREPARATION (60-70% waktu kerja analis) ===")
masalah = {"kosong": int(df.cangkir.isna().sum()), "negatif": int((df.cangkir < 0).sum())}
df.loc[df.cangkir < 0, "cangkir"] = np.nan
q1, q3 = df.cangkir.quantile([.25, .75]); iqr = q3 - q1
out = df.cangkir > q3 + 3 * iqr
masalah["outlier"] = int(out.sum())
df.loc[out, "cangkir"] = np.nan
df["cangkir"] = df.cangkir.fillna(df.cangkir.median())
print("Masalah ditemukan & diperbaiki:", masalah)

print("\n=== 1. DESCRIPTIVE: apa yang terjadi? ===")
print(f"Total terjual : {df.cangkir.sum():,.0f} cangkir | Rata-rata/hari: {df.cangkir.mean():.1f}")
print(df.groupby(df.tanggal.dt.to_period("M")).cangkir.mean().round(1).to_string())

print("\n=== 2. DIAGNOSTIC: mengapa terjadi? ===")
dp = df.groupby("promo").cangkir.mean(); dw = df.groupby("akhir_pekan").cangkir.mean()
print(f"Promo    : tanpa={dp[0]:.1f} | dengan={dp[1]:.1f}")
print(f"Weekend  : weekday={dw[0]:.1f} | weekend={dw[1]:.1f}")

print("\n=== 3. PREDICTIVE: apa yang akan terjadi? ===")
df["t"] = np.arange(N)
fit = ["promo", "akhir_pekan", "t"]
tr, te = df.iloc[:150], df.iloc[150:]
m = LinearRegression().fit(tr[fit], tr.cangkir)
mae = np.abs(m.predict(te[fit]) - te.cangkir).mean()
print(f"MAE data uji (30 hari terakhir): {mae:.2f} cangkir")
m = LinearRegression().fit(df[fit], df.cangkir)
fut_tgl = pd.date_range(tgl[-1] + pd.Timedelta(days=1), periods=7)
fut = pd.DataFrame({"promo": 0, "akhir_pekan": (fut_tgl.dayofweek >= 5).astype(int), "t": np.arange(N, N + 7)})
fut["prediksi"] = m.predict(fut[fit])

print("\n=== 4. PRESCRIPTIVE: apa yang harus dilakukan? ===")
KAPASITAS, MARGIN, BIAYA_PROMO = 170, 8000, 150000
uplift = m.coef_[0]
fut["tambahan"] = np.clip(np.minimum(uplift, KAPASITAS - fut.prediksi), 0, None)
fut["untung_promo"] = fut.tambahan * MARGIN - BIAYA_PROMO
fut["rekomendasi"] = np.where(fut.untung_promo > 0, "PROMO", "tanpa promo")
fut.index = fut_tgl.strftime("%a %d-%b")
print(f"(efek promo model: +{uplift:.1f} cangkir, kapasitas {KAPASITAS}/hari)")
print(fut[["prediksi", "untung_promo", "rekomendasi"]].round(0).to_string())

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(df.tanggal, df.cangkir, color="#4C72B0", lw=1, label="Aktual (bersih)")
ax[0].plot(fut_tgl, fut.prediksi, "o-", color="#C44E52", label="Prediksi 7 hari")
ax[0].set_title("Predictive: tren & prediksi"); ax[0].legend(); ax[0].tick_params(axis="x", rotation=30)
ax[1].bar(["Weekday", "Weekend", "Tanpa promo", "Promo"], [dw[0], dw[1], dp[0], dp[1]],
          color=["#8da0cb", "#8da0cb", "#a6d854", "#a6d854"])
ax[1].set_title("Diagnostic: pendorong penjualan"); ax[1].set_ylabel("Rata-rata cangkir/hari")
plt.tight_layout(); plt.savefig("sesi1_piramida_analitik/hasil.png", dpi=130)
