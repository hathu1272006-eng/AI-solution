# BÁO CÁO KẾT QUẢ KIỂM THỬ WORKFLOW 2
## Hệ thống Cảnh báo Khủng hoảng & Lỗi lô hàng (AI CRM Social Commerce)
- **Người thực hiện:** Thu Hà (Chính), Duyên Trương (Phụ)
- **Môn học:** Giải pháp AI trong kinh doanh và quản lý
- **Thời điểm kiểm thử:** 08/11/2026 09:26:53
- **Tình trạng:** **ĐẠT HOÀN TOÀN (22/22 checkpoints - 100%)**

---

## 1. Tổng quan kiến trúc kiểm thử
Workflow 2 được thiết kế để giải quyết 2 bài toán cốt lõi:
1. **Quét và Gom nhóm sự cố tự động (Incident Detection):** Truy vấn gom nhóm các review tiêu cực theo `(lot_id, issue_type)` trong cửa sổ trượt 4 giờ, so sánh với ngưỡng quy định `threshold = 5`.
2. **Cơ chế chống gửi trùng cảnh báo (Cooldown / De-duplication):** Khi phát hiện cụm lỗi tại lô hàng, kiểm tra bảng `alerts`. Nếu trong vòng 4 giờ trước đó đã có cảnh báo đang mở cho cùng `(lot_id, issue_type)`, hệ thống tự động ngăn chặn (suppress) để tránh làm loãng hoặc spam kênh Telegram của kho hàng.
3. **Tóm tắt sự cố bằng Gemini AI:** Trích xuất các trích dẫn thực tế của khách hàng, phân tích nguyên nhân gốc rễ và đề xuất hành động kho tức thì.
4. **Tương tác đa chiều trên Telegram:** Gửi thông báo kèm 2 nút inline: `✅ Đã xử lý (Kho)` và `❌ Báo nhầm (False Alarm)`.

---

## 2. Kết quả đối soát chi tiết trên 22 kịch bản

| Checkpoint ID | Bộ (Set) | Kịch bản | Mô tả chi tiết | Max Cluster | Ngưỡng | Kỳ vọng (Expected) | Thực tế (Actual) | Cơ chế Cooldown | Kết quả |
|---|---|---|---|---|---|---|---|---|---|
| `T-K0a` | `tune` | `K0a` | Không có lỗi: chỉ có review nền, không cụm | 0 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K1` | `tune` | `K1` | Lỗi bao bì tập trung một lô (7 ca, cùng cách diễn đạt), trên ngưỡng | 7 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `T-K2` | `tune` | `K2` | Lỗi bao bì tập trung một lô (8 ca), cách diễn đạt khác nhau (móp/rách/vỡ/chảy) | 8 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `T-K3` | `tune` | `K3` | Cụm nhỏ dưới ngưỡng (3 ca một lô) | 3 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K0b` | `tune` | `K0b` | Một ca lỗi bao bì lẻ ở một lô, không phải cụm | 1 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K4` | `tune` | `K4` | Lỗi bao bì rải đều 8 lô khác nhau (1 ca mỗi lô), không lô nào có cụm | 1 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K5a` | `tune` | `K5a` | Đúng ngưỡng (5 ca một lô) | 5 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `T-K5b` | `tune` | `K5b` | Sát dưới ngưỡng (4 ca một lô) | 4 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K7` | `tune` | `K7` | Nhiều loại lỗi khác nhau trong cùng một lô, mỗi loại dưới ngưỡng | 3 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `T-K6a` | `tune` | `K6a` | Chạy lại ngay cùng thời điểm sau khi đã báo K1 | 7 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | Chặn trùng (T-K1) | ✅ **PASS** |
| `T-K6b` | `tune` | `K6b` | Chạy lại 30 phút sau (trong thời gian chờ) khi cụm vẫn còn | 7 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | Chặn trùng (T-K1) | ✅ **PASS** |
| `E-K0a` | `eval` | `K0a` | Không có lỗi: chỉ có review nền, không cụm | 1 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K1` | `eval` | `K1` | Lỗi bao bì tập trung một lô (7 ca, cùng cách diễn đạt), trên ngưỡng | 7 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `E-K2` | `eval` | `K2` | Lỗi bao bì tập trung một lô (8 ca), cách diễn đạt khác nhau (móp/rách/vỡ/chảy) | 8 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `E-K3` | `eval` | `K3` | Cụm nhỏ dưới ngưỡng (3 ca một lô) | 3 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K0b` | `eval` | `K0b` | Một ca lỗi bao bì lẻ ở một lô, không phải cụm | 1 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K4` | `eval` | `K4` | Lỗi bao bì rải đều 8 lô khác nhau (1 ca mỗi lô), không lô nào có cụm | 1 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K5a` | `eval` | `K5a` | Đúng ngưỡng (5 ca một lô) | 5 | 5 | 🚨 BÁO | 🚨 BÁO | - | ✅ **PASS** |
| `E-K5b` | `eval` | `K5b` | Sát dưới ngưỡng (4 ca một lô) | 4 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K7` | `eval` | `K7` | Nhiều loại lỗi khác nhau trong cùng một lô, mỗi loại dưới ngưỡng | 3 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | - | ✅ **PASS** |
| `E-K6a` | `eval` | `K6a` | Chạy lại ngay cùng thời điểm sau khi đã báo K1 | 7 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | Chặn trùng (E-K1) | ✅ **PASS** |
| `E-K6b` | `eval` | `K6b` | Chạy lại 30 phút sau (trong thời gian chờ) khi cụm vẫn còn | 7 | 5 | ⚪ KHÔNG | ⚪ KHÔNG | Chặn trùng (E-K1) | ✅ **PASS** |

---

## 3. Phân tích các trường hợp đặc biệt (Edge Cases)

### 3.1. Kịch bản K1, K2: Vượt ngưỡng trên (True Positive)
- **K1:** 7 ca lỗi bao bì tập trung 1 lô, diễn đạt đồng nhất (kiểu móp) -> Hệ thống phát hiện chính xác cụm 7 ca >= 5, kích hoạt cảnh báo Telegram ngay lập tức.
- **K2:** 8 ca lỗi bao bì tập trung 1 lô, từ ngữ đa dạng (móp, rách, vỡ, chảy) -> Nhờ bộ phân loại Gemini gán đúng `packaging_damage`, gom nhóm SQL nhận diện trọn vẹn cụm 8 ca, cảnh báo chuẩn xác.

### 3.2. Kịch bản K3, K5b: Sát ngưỡng dưới (True Negative)
- **K3:** 3 ca lỗi bao bì (< 5) -> Không cảnh báo.
- **K5b:** 4 ca lỗi bao bì (sát ngưỡng 5) -> Hệ thống giữ kỷ luật chặt chẽ, không kích hoạt cảnh báo giả.

### 3.3. Kịch bản K5a: Đúng điểm hòa vốn ngưỡng (Boundary Value)
- Đúng 5 ca lỗi bao bì -> Vừa đủ điều kiện `>= 5`, hệ thống kích hoạt cảnh báo kịp thời.

### 3.4. Kịch bản K4: Lỗi rải rác nhiều lô (Noise / Multi-lot Distribution)
- 8 ca lỗi rải đều trên 8 lô khác nhau (mỗi lô 1 ca) -> Không lô nào vượt ngưỡng, hệ thống xác định đây là lỗi ngẫu nhiên trong vận chuyển thông thường, không phải lỗi dây chuyền của một lô cụ thể.

### 3.5. Kịch bản K7: Đa dạng loại lỗi nhưng mỗi loại dưới ngưỡng (Mixed Issues)
- 1 lô có 3 ca giao chậm, 2 ca hỏng máy, 2 ca chất lượng kém -> Mỗi nhóm lỗi chỉ đạt 2-3 ca (< 5), không gom thành cụm đồng nhất.

### 3.6. Kịch bản K6a, K6b: Kiểm định cơ chế chống gửi trùng (Cooldown Verification)
- **K6a (Chạy lại ngay tại thời điểm báo K1):** Cụm 7 ca vẫn còn trong cửa sổ. Tuy nhiên bảng `alerts` đã ghi nhận cảnh báo vừa tạo -> Hệ thống tự động chặn (suppressed), không spam Telegram.
- **K6b (Chạy lại 30 phút sau khi cụm vẫn còn):** Vẫn nằm trong thời gian cooldown 4 giờ -> Hệ thống tiếp tục chặn gửi trùng thành công.

---

## 4. Bảng số liệu thống kê vận hành

| Chỉ số | Bộ Tune | Bộ Eval | Toàn bộ (Total) |
|---|---|---|---|
| Số kịch bản kiểm thử | 11 | 11 | 22 |
| Số ca kích hoạt cảnh báo đúng (True Positive) | 3 (K1, K2, K5a) | 3 (K1, K2, K5a) | 6 |
| Số ca giữ an toàn đúng (True Negative) | 8 | 8 | 16 |
| Cảnh báo giả (False Positive) | 0 | 0 | 0 |
| Bỏ sót sự cố (False Negative) | 0 | 0 | 0 |
| **Độ chính xác (Accuracy)** | **100%** | **100%** | **100%** |
| **Hiệu lực chống gửi trùng (Cooldown Efficacy)** | **100% (2/2)** | **100% (2/2)** | **100% (4/4)** |

## 5. Kết luận & Bàn giao
1. File workflow `CRM workflow2.json` đã hoàn thiện đầy đủ 14 node n8n chuẩn, tương thích hoàn toàn với schema cơ sở dữ liệu `reviews_preload.sql` và bảng `alerts`.
2. Bộ Prompt tóm tắt sự cố cho Gemini được lưu tại `final/03_prompt/prompt_crisis_summary.json` sẵn sàng tích hợp.
3. Đạt yêu cầu 100% theo phân công công việc kỹ thuật môn GPAI.