#!/usr/bin/env python3
"""stl/*.stl dosyalarının matplotlib PNG önizlemesi (onizleme/stl-*.png)."""
import glob, os, struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))


def oku(yol):
    with open(yol, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        a = np.frombuffer(f.read(50 * n), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return a["v"].astype(float), a["n"].astype(float)


def ciz(ax, V, N, elev, azim, baslik):
    isik = np.array([0.4, -0.5, 0.75]); isik /= np.linalg.norm(isik)
    sh = np.clip(N @ isik, 0, 1) * 0.6 + 0.3
    col = np.stack([sh * 0.62, sh * 0.64, sh * 0.68, np.ones_like(sh)], axis=1)
    pc = Poly3DCollection(V, facecolors=col, edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    mn, mx = V.reshape(-1, 3).min(0), V.reshape(-1, 3).max(0)
    c = (mn + mx) / 2; r = (mx - mn).max() / 2 * 1.02
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(baslik, fontsize=9)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("x (mm)", fontsize=7); ax.set_ylabel("y (mm)", fontsize=7); ax.set_zlabel("z (mm)", fontsize=7)


def main():
    dosyalar = sorted(glob.glob(os.path.join(HERE, "stl", "*.stl")))
    fig_all = plt.figure(figsize=(15, 9), dpi=90)
    for i, d in enumerate(dosyalar):
        V, N = oku(d)
        ad = os.path.basename(d)[:-4]
        mn, mx = V.reshape(-1, 3).min(0), V.reshape(-1, 3).max(0)
        bilgi = f"{ad}.stl  {len(V)} üçgen  boyut {mx[0]-mn[0]:.1f}×{mx[1]-mn[1]:.1f}×{mx[2]-mn[2]:.1f} mm"
        fig = plt.figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(1, 2, 1, projection="3d"); ciz(ax, V, N, 28, -55, bilgi)
        ax2 = fig.add_subplot(1, 2, 2, projection="3d"); ciz(ax2, V, N, 90, -90, "üstten")
        fig.tight_layout(); fig.savefig(os.path.join(HERE, "onizleme", f"stl-{ad}.png")); plt.close(fig)
        a = fig_all.add_subplot(2, 3, i + 1, projection="3d"); ciz(a, V, N, 28, -55, ad)
    fig_all.tight_layout(); fig_all.savefig(os.path.join(HERE, "onizleme", "stl-hepsi.png")); plt.close(fig_all)
    print("stl önizlemeleri tamam:", len(dosyalar))


if __name__ == "__main__":
    main()
