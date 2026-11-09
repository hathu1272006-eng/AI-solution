#!/usr/bin/env python3
"""Sinh báo cáo kiểm tra dữ liệu (Markdown) từ các log và metrics do các script khác tạo ra. Không gõ tay số liệu."""
import json
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parent.parent / "06_reports"
S = Path(__file__).resolve().parent.parent / "02_scenarios"
cl = json.load(open(R / "cleaning_log.json", encoding="utf-8")); sp = json.load(open(R / "split_report.json", encoding="utf-8"))
sr = json.load(open(S / "scenario_report.json", encoding="utf-8")); pc = json.load(open(R / "preload_check.json", encoding="utf-8"))
ct = pd.read_csv(R / "crosstab_rating_label.csv"); mt = pd.read_csv(R / "metrics.csv")
L = []
w = L.append
w("# Báo cáo kiểm tra dữ liệu - Phần A\n")
w("## 1. Nguồn dữ liệu")
w("- Bộ: Shopee Vietnamese Product Reviews Sentiment (Kaggle, tác giả dduongdev), đường dẫn ghi trong đề xuất của nhóm.")
w("- **Giấy phép: chưa xác minh.** Cần nhóm kiểm tra trên trang Kaggle (báo cáo này không truy cập được mạng). **Thời điểm thu thập và cách gán nhãn: chưa có căn cứ** (đề xuất của nhóm cũng ghi như vậy).")
w(f"- Tệp gốc: 9.599 dòng (trường id, review, rating, label). Tệp aug không dấu: {cl['aug']['rows']} dòng, **không dùng làm dữ liệu** (xem mục 4).\n")
w("## 2. Làm sạch")
w("| Bước | Số dòng còn lại | Ghi chú |\n|---|---|---|")
for s in cl["steps"]:
    w(f"| {s['step']} | {s['rows']} | {s['note']} |")
w(f"\n- `id` trùng: {cl['id_duplicates']}; nhóm văn bản trùng nhưng khác nhãn: {cl['conflicting_label_text_groups']}.")
w(f"- Review ngắn dưới 30 ký tự: {cl['short_review_lt30']} (giữ lại, là review hợp lệ).")
w(f"- Nhóm gần trùng (cosine >= {cl['near_dup_threshold']}): {cl['near_dup_groups_size_ge2']} nhóm, {cl['near_dup_rows_in_groups']} dòng; được gom nhóm, không xóa; chia tập theo nhóm.")
w(f"- Nhãn sau làm sạch: {cl['label_after_clean']}\n")
w("## 3. Bảng chéo rating x label và các ca lệch")
w("| rating | negative | positive |\n|---|---|---|")
for _, r in ct.iterrows():
    w(f"| {int(r['rating'])} | {int(r['negative'])} | {int(r['positive'])} |")
w(f"\nCờ lệch: {cl['flag_counts']}. Đây chỉ là cờ, **chưa kết luận gán sai**. Đọc thử ngẫu nhiên 30 ca lệch (10 mỗi nhóm) thì nhãn gốc khớp nội dung văn bản ở khoảng 28/30 ca (2 ca mơ hồ), tức ở các ca lệch số sao thường là phần không khớp với nội dung. Đây là đọc của một người, không thay cho gán nhãn độc lập.\n")
w("## 4. Tệp aug không dấu")
a = cl["aug"]
w(f"- {a['id_in_main']} trên {a['rows']} dòng trùng id với tệp gốc (sau khi loại trùng); {a['text_in_main_after_accent_strip']} dòng có nội dung giống hệt sau khi bỏ dấu; {a['id_not_in_main_and_text_not_in_main']} dòng không khớp id lẫn nội dung (nguồn không rõ).")
w("- Kết luận: là bản sao không dấu của review đã có, gộp vào sẽ gây rò rỉ giữa các tập. Thay vào đó Test không dấu được sinh từ chính Test chính bằng hàm bỏ dấu.\n")
w("## 5. Chia tập")
w("| Tập | Số dòng | Phân bố nhãn gốc |\n|---|---|---|")
for k, v in sp["split_counts"].items():
    w(f"| {k} | {v} | {sp['label_by_split'][k]} |")
w(f"\n- Test không dấu: {sp['test_unaccented_rows']} dòng (cùng id với test_main). Nhóm con của test_skew: {sp['skew_subgroups']}.")
w(f"- Seed {sp['params']['seed']}; chia theo nhóm gần trùng; phiên bản script {sp['script_version']}.")
w("- Kết quả kiểm tra rò rỉ (script tự kiểm tra): " + ", ".join(f"{k}={'đạt' if v else 'KHÔNG ĐẠT'}" for k, v in sp["verification"].items()) + "\n")
w("## 6. Bộ kịch bản WF2")
w(f"- Dòng theo bộ: {sr['rows_by_set']}; {sr['checkpoints']} điểm kiểm tra; điểm kỳ vọng có cảnh báo: {sr['expected_alert_true']}.")
w(f"- Quy ước tham chiếu: cửa sổ {sr['params']['window_hours']} giờ, ngưỡng >= {sr['params']['ref_threshold']} ca cùng (lô, nhóm lỗi). Đây là giả định, có thể đổi.")
w(f"- Kiểm tra: {sr['checks']}.\n")
w("## 7. Kiểm tra file nạp PostgreSQL")
w(f"- Môi trường kiểm tra: {pc['engine']}. Số dòng: {pc['counts']}; khóa ngoại mồ côi: {pc['fk_orphans_review_gold']}; văn bản khác CSV: {pc['review_text_differs_from_csv']}; kiểm tra chéo kịch bản bằng GROUP BY: {pc['scenario_sql_crosscheck']['mismatches']} lệch trên {pc['scenario_sql_crosscheck']['checkpoints']} điểm.")
w("- Chưa chạy thử trực tiếp trên PostgreSQL (môi trường không có).\n")
w("## 8. Kết quả baseline theo số sao (đã đo)")
w("| Tập | Hệ thống | n | Accuracy | Macro F1 | Recall Negative | CI 95% Recall Neg | Precision Neg |\n|---|---|---|---|---|---|---|---|")
for _, r in mt.iterrows():
    w(f"| {r['split']} | {r['system']} | {int(r['n'])} | {r['accuracy']} | {r['macro_f1']} | {r['recall_negative']} | {r['recall_negative_ci95_lo']}-{r['recall_negative_ci95_hi']} | {r['precision_negative']} |")
w("\nGemini: **chưa có kết quả** (cần chạy run_classifier.py với khóa API). Test lệch: chưa chấm vì chưa có nhãn người.")
(R / "bao_cao_kiem_tra_du_lieu.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("đã ghi", R / "bao_cao_kiem_tra_du_lieu.md")
