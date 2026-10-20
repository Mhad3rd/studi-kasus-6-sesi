"""Sesi 2 - HPC untuk masalah lokal: prediksi risiko polusi udara 7 hari (Monte Carlo)
dihitung SERIAL vs PARALEL. Mensimulasikan ide 'memangkas waktu komputasi'."""
import time, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from multiprocessing import Pool

def prob_melebihi(seed, sims=20000, jam=168, ambang=55):
    """Peluang PM2.5 sel grid melewati ambang dalam 7 hari (168 jam)."""
    rng = np.random.default_rng(seed)
    awal = rng.uniform(20, 45)
    jalan = awal + np.cumsum(rng.normal(0, 2.5, (sims, jam)), axis=1)
    return float((jalan.max(axis=1) > ambang).mean())

def jalankan(n_sel, workers):
    t0 = time.perf_counter()
    if workers == 1:
        hasil = [prob_melebihi(s) for s in range(n_sel)]
    else:
        with Pool(workers) as p:
            hasil = p.map(prob_melebihi, range(n_sel))
    return time.perf_counter() - t0, hasil

if __name__ == "__main__":
    N_SEL = 64
    cpu = os.cpu_count() or 1
    daftar = sorted({1, 2, 4, cpu})
    print(f"CPU tersedia: {cpu} | jumlah sel grid: {N_SEL}")
    baris, ref = [], None
    for w in daftar:
        dt, hasil = jalankan(N_SEL, w)
        ref = ref or dt
        baris.append({"workers": w, "waktu_detik": round(dt, 2), "speedup": round(ref / dt, 2)})
        print(baris[-1])
    df = pd.DataFrame(baris); df.to_csv("sesi2_hpc_paralel/hasil_benchmark.csv", index=False)
    risiko = np.array(hasil).reshape(8, 8)
    print(f"Sel risiko tertinggi: {risiko.max():.1%} | rata-rata: {risiko.mean():.1%}")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(df.workers, df.speedup, "o-", color="#4C72B0", label="Aktual")
    ax[0].plot(df.workers, df.workers, "--", color="gray", label="Ideal")
    ax[0].set_xlabel("Jumlah proses"); ax[0].set_ylabel("Speedup (x)"); ax[0].legend(); ax[0].set_title("Serial vs Paralel")
    im = ax[1].imshow(risiko, cmap="YlOrRd"); ax[1].set_title("Peta risiko polusi 7 hari (8x8 sel)")
    plt.colorbar(im, ax=ax[1], label="Peluang > ambang"); plt.tight_layout()
    plt.savefig("sesi2_hpc_paralel/hasil.png", dpi=130)
