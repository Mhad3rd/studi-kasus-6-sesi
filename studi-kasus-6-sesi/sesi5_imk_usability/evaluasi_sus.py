"""Sesi 5 - IMK: evaluasi usability dua prototipe (A=lama, B=baru) memakai SUS + Think-Aloud (data sintetis)."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(3)
def kuesioner(n, mu):
    """10 item SUS skala 1-5; item ganjil positif, genap negatif."""
    s = rng.normal(mu, .6, n); out = np.zeros((n, 10), int)
    for j in range(10):
        v = s + rng.normal(0, .6, n) if j % 2 == 0 else 6 - s + rng.normal(0, .6, n)
        out[:, j] = np.clip(np.round(v), 1, 5)
    return out

def skor_sus(m):
    ganjil, genap = m[:, 0::2] - 1, 5 - m[:, 1::2]
    return (ganjil.sum(1) + genap.sum(1)) * 2.5

def nilai(s):
    return "Excellent" if s >= 85 else "Good" if s >= 73 else "Okay (di atas rata-rata)" if s >= 68 else "Poor" if s >= 51 else "Awful"

n = 12
sus = {"A (lama)": skor_sus(kuesioner(n, 2.9)), "B (baru)": skor_sus(kuesioner(n, 4.1))}
print("=== SUS (benchmark rata-rata = 68) ===")
for k, v in sus.items():
    print(f"Prototipe {k}: rata-rata={v.mean():.1f} (SD {v.std(ddof=1):.1f}) -> {nilai(v.mean())}")
t, p = stats.ttest_ind(sus["B (baru)"], sus["A (lama)"], equal_var=False)
print(f"Welch t-test: t={t:.2f}, p={p:.4f} -> {'perbedaan signifikan' if p < .05 else 'tidak signifikan'}")

print("\n=== Think-Aloud Protocol (per peserta) ===")
ta = pd.DataFrame({"versi": ["A"] * n + ["B"] * n,
                   "error": np.r_[rng.poisson(3.0, n), rng.poisson(1.0, n)],
                   "waktu_detik": np.r_[rng.normal(95, 12, n), rng.normal(60, 9, n)].round()})
print(ta.groupby("versi").agg(rata_error=("error", "mean"), rata_waktu=("waktu_detik", "mean")).round(1).to_string())
ta.to_csv("sesi5_imk_usability/data_think_aloud.csv", index=False)

fig, ax = plt.subplots(1, 3, figsize=(13, 4))
ax[0].boxplot(list(sus.values()), tick_labels=list(sus.keys())); ax[0].axhline(68, ls="--", color="red", label="Rata-rata 68"); ax[0].legend(); ax[0].set_title("Skor SUS")
ta.boxplot(column="error", by="versi", ax=ax[1], grid=False); ax[1].set_title("Jumlah error / peserta"); ax[1].set_xlabel("")
ta.boxplot(column="waktu_detik", by="versi", ax=ax[2], grid=False); ax[2].set_title("Waktu selesai tugas (detik)"); ax[2].set_xlabel("")
plt.suptitle(""); plt.tight_layout(); plt.savefig("sesi5_imk_usability/hasil.png", dpi=130)
