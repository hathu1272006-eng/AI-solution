# Phần A - Dữ liệu và phân loại: sản phẩm cuối

Đọc trước: `Tai_lieu_thuc_hien_PhanA.docx` (quá trình, giải thích sản phẩm, số liệu, hạn chế, việc cần làm).

| Thư mục | Nội dung |
|---|---|
| 01_data | reviews.csv (bảng reviews nạp sẵn), review_gold.csv (nhãn, tập chia), test_unaccented.csv, shopee_clean.csv, data_dictionary.xlsx, preload/schema.sql, preload/reviews_preload.sql |
| 02_scenarios | scenario_reviews.csv, scenario_checkpoints.csv, scenario_report.json (kịch bản WF2, hai bộ tune/eval) |
| 03_prompt | prompt_v1/v2/v3.json, output_schema.json, issue_type_catalog.json, fewshot_examples.json |
| 04_labeling | 4 phiếu gán nhãn Test lệch, huong_dan_gan_nhan.md |
| 05_scripts | Toàn bộ script; run_pipeline.sh dựng lại dữ liệu từ hai tệp gốc |
| 06_reports | bao_cao_kiem_tra_du_lieu.md, metrics.csv (baseline), confusion_*.png, errors_*.csv, log làm sạch/chia tập |

Chưa có (cần chạy ngoài môi trường này): kết quả Gemini, nhãn người cho Test lệch, phân tích lỗi của Gemini.
Dựng lại: `bash 05_scripts/run_pipeline.sh <thư mục chứa shopee_reviews_dataset.jsonl và aug_unaccented_reviews.jsonl>`
Chạy Gemini: xem mục 2 của tài liệu Word.
