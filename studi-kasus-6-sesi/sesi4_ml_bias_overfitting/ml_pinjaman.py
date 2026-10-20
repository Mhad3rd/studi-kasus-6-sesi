"""Sesi 4 - Machine Learning: (a) overfitting vs underfitting, (b) bias data pada persetujuan pinjaman."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(1)
n = 3000
grup = rng.choice(["A", "B"], n)
pendapatan = rng.normal(0, 1, n) - 0.3 * (grup == "B")   # proxy: grup B rata-rata pendapatan lebih rendah
skor = rng.normal(0, 1, n); utang = rng.normal(0, 1, n)
layak = (0.8 * pendapatan + 1.0 * skor - 0.8 * utang + rng.normal(0, 0.5, n)) > 0
label = layak & ~((grup == "B") & (rng.random(n) < 0.30))  # BIAS historis: 30% pemohon layak grup B ditolak
df = pd.DataFrame({"pendapatan": pendapatan, "skor_kredit": skor, "rasio_utang": utang,
                   "grup_B": (grup == "B").astype(int), "disetujui": label.astype(int)})
X, y = df.drop(columns="disetujui"), df.disetujui
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.3, random_state=0)

print("=== A. Overfitting vs Underfitting (Decision Tree) ===")
kedalaman = [1, 2, 3, 5, 8, 12, 20]; acc_tr, acc_te = [], []
for d in kedalaman:
    t = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
    acc_tr.append(t.score(Xtr, ytr)); acc_te.append(t.score(Xte, yte))
    print(f"depth={d:>2} | train={acc_tr[-1]:.3f} | test={acc_te[-1]:.3f} | gap={acc_tr[-1]-acc_te[-1]:+.3f}")

print("\n=== B. Audit Bias (Logistic Regression) ===")
def audit(nama, kolom):
    m = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr[kolom], ytr)
    pred = m.predict(Xte[kolom]); g = Xte.grup_B.values
    a, b = pred[g == 0].mean(), pred[g == 1].mean()
    print(f"{nama:<28} acc={np.mean(pred == yte):.3f} | setuju A={a:.1%} B={b:.1%} | disparate impact={b/a:.2f} {'(BIAS <0.80)' if b/a < .8 else '(OK)'}")
    return a, b
r1 = audit("Dengan atribut grup", list(X.columns))
r2 = audit("Tanpa atribut grup", ["pendapatan", "skor_kredit", "rasio_utang"])

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(kedalaman, acc_tr, "o-", label="Train", color="#4C72B0"); ax[0].plot(kedalaman, acc_te, "o-", label="Test", color="#C44E52")
ax[0].set_xlabel("Kedalaman pohon"); ax[0].set_ylabel("Akurasi"); ax[0].legend(); ax[0].set_title("Underfit -> Pas -> Overfit")
x = np.arange(2); ax[1].bar(x - .18, r1, .36, label="Dengan atribut grup"); ax[1].bar(x + .18, r2, .36, label="Tanpa atribut grup")
ax[1].set_xticks(x); ax[1].set_xticklabels(["Grup A", "Grup B"]); ax[1].set_ylabel("Tingkat persetujuan"); ax[1].legend(); ax[1].set_title("Audit bias persetujuan")
plt.tight_layout(); plt.savefig("sesi4_ml_bias_overfitting/hasil.png", dpi=130)
