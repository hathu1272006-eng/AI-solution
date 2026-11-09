#!/usr/bin/env python3
"""Gộp phiếu gán nhãn đã điền, tính Cohen's kappa cho từng cặp, xuất danh sách bất đồng để thống nhất.
Bước 1: python compute_kappa.py --dir ../04_labeling      -> kappa + to_reconcile.csv
Bước 2: điền cột final_label trong to_reconcile.csv (hai người bàn bạc), rồi chạy lại với --finalize
        -> human_labels_final.csv (cột review_id, label_human) dùng cho evaluate.py --human
Quy ước: label chỉ nhận positive|negative; ô trống hoặc unsure=1 được đưa vào danh sách thống nhất, và KHÔNG tính vào kappa.
"""
import argparse
from pathlib import Path
import pandas as pd

LAB = {"positive", "negative"}

def kappa(x, y):
    n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    pe = sum((sum(a == c for a in x) / n) * (sum(b == c for b in y) / n) for c in LAB)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe), po

def load(p):
    d = pd.read_csv(p, dtype={"review_id": str}).fillna("")
    d["label"] = d["label"].str.strip().str.lower()
    return d.set_index("review_id")

def main(a):
    D = Path(a.dir); rep = []; recon = []
    for name, (r1, r2) in {"nua1": ("rater1", "rater2"), "nua2": ("rater3", "rater4")}.items():
        p1, p2 = D / f"phieu_gan_nhan_{name}_{r1}.csv", D / f"phieu_gan_nhan_{name}_{r2}.csv"
        A, B = load(p1), load(p2)
        ids = A.index.intersection(B.index)
        ok = [i for i in ids if A.at[i, "label"] in LAB and B.at[i, "label"] in LAB and str(A.at[i, "unsure"]) != "1" and str(B.at[i, "unsure"]) != "1"]
        if ok:
            k, po = kappa([A.at[i, "label"] for i in ok], [B.at[i, "label"] for i in ok])
            rep.append({"cap": f"{r1}-{r2}", "n_total": len(ids), "n_tinh_kappa": len(ok), "ti_le_dong_y": round(po, 4), "cohen_kappa": round(k, 4)})
        for i in ids:
            la, lb = A.at[i, "label"], B.at[i, "label"]
            if la != lb or la not in LAB or str(A.at[i, "unsure"]) == "1" or str(B.at[i, "unsure"]) == "1":
                recon.append({"review_id": i, "review_text": A.at[i, "review_text"], "label_a": la, "label_b": lb, "final_label": "", "ly_do": ""})
    pd.DataFrame(rep).to_csv(D / "kappa_report.csv", index=False, encoding="utf-8")
    print(pd.DataFrame(rep).to_string(index=False))
    rc = D / "to_reconcile.csv"
    if not a.finalize:
        pd.DataFrame(recon).to_csv(rc, index=False, encoding="utf-8-sig")
        print("Số ca cần thống nhất:", len(recon), "->", rc)
        return
    fin = pd.read_csv(rc, dtype={"review_id": str}).fillna("")
    assert fin["final_label"].str.strip().str.lower().isin(LAB).all(), "còn ca chưa có final_label hợp lệ"
    fin_map = dict(zip(fin["review_id"], fin["final_label"].str.strip().str.lower()))
    out = []
    for name, (r1, r2) in {"nua1": ("rater1", "rater2"), "nua2": ("rater3", "rater4")}.items():
        A = load(D / f"phieu_gan_nhan_{name}_{r1}.csv")
        B = load(D / f"phieu_gan_nhan_{name}_{r2}.csv")
        for i in A.index.intersection(B.index):
            out.append({"review_id": i, "label_human": fin_map.get(i, A.at[i, "label"])})
    pd.DataFrame(out).to_csv(D / "human_labels_final.csv", index=False, encoding="utf-8")
    print("Đã ghi", len(out), "nhãn người ->", D / "human_labels_final.csv")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent.parent / "04_labeling"))
    ap.add_argument("--finalize", action="store_true")
    main(ap.parse_args())
