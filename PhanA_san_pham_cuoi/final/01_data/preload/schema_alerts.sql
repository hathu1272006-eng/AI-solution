-- ==============================================================================
-- Schema Bảng alerts cho Workflow 2: Cảnh báo Khủng hoảng & Lỗi lô hàng
-- Tác giả: Thu Hà (Chính), Duyên Trương (Phụ)
-- Đề tài: Hệ thống AI CRM và cảnh báo rủi ro đơn hàng đa kênh (Social Commerce)
-- Môn: Giải pháp AI trong kinh doanh và quản lý
-- ==============================================================================

-- Bảng alerts lưu trữ lịch sử các sự cố cụm lỗi lô hàng vượt ngưỡng
CREATE TABLE IF NOT EXISTS alerts (
  alert_id            SERIAL PRIMARY KEY,
  lot_id              TEXT NOT NULL,
  issue_type          TEXT NOT NULL REFERENCES issue_types(issue_type),
  product_id          TEXT,
  cluster_size        INTEGER NOT NULL,
  threshold           INTEGER NOT NULL DEFAULT 5,
  window_start        TIMESTAMPTZ NOT NULL,
  window_end          TIMESTAMPTZ NOT NULL,
  sim_now             TIMESTAMPTZ NOT NULL,
  incident_summary    TEXT,
  root_cause          TEXT,
  evidence            TEXT,
  severity            TEXT NOT NULL DEFAULT 'CRITICAL' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
  status              TEXT NOT NULL DEFAULT 'alerted' CHECK (status IN ('alerted', 'investigating', 'resolved', 'false_alarm')),
  telegram_message_id TEXT,
  channel             TEXT DEFAULT 'warehouse_qc',
  resolved_by         TEXT,
  resolved_at         TIMESTAMPTZ,
  notes               TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Chỉ mục hỗ trợ kiểm tra Cooldown (chống gửi trùng cảnh báo trong khung thời gian 4h)
CREATE INDEX IF NOT EXISTS idx_alerts_cooldown 
ON alerts (lot_id, issue_type, status, created_at);

-- Chỉ mục phục vụ dashboard quản trị và theo dõi xử lý khủng hoảng
CREATE INDEX IF NOT EXISTS idx_alerts_status_created 
ON alerts (status, created_at DESC);

-- Ghi chú chú thích các cột
COMMENT ON TABLE alerts IS 'Lưu trữ các cảnh báo khủng hoảng lỗi sản phẩm theo lô do Workflow 2 tạo ra';
COMMENT ON COLUMN alerts.alert_id IS 'Mã định danh cảnh báo (Khóa chính tự tăng)';
COMMENT ON COLUMN alerts.lot_id IS 'Mã lô hàng phát hiện sự cố (ví dụ: L03-2, L05-1)';
COMMENT ON COLUMN alerts.issue_type IS 'Loại sự cố chính theo danh mục issue_types (ví dụ: packaging_damage)';
COMMENT ON COLUMN alerts.cluster_size IS 'Số lượng đánh giá tiêu cực ghi nhận trong cửa sổ giám sát';
COMMENT ON COLUMN alerts.threshold IS 'Ngưỡng tham chiếu kích hoạt cảnh báo (mặc định 5 ca/4h)';
COMMENT ON COLUMN alerts.sim_now IS 'Thời điểm phát hiện cảnh báo (thực tế hoặc thời điểm giả lập trong test)';
COMMENT ON COLUMN alerts.incident_summary IS 'Tóm tắt sự cố do Gemini AI phân tích từ nội dung review';
COMMENT ON COLUMN alerts.root_cause IS 'Giả thuyết nguyên nhân gốc rễ (đóng gói, bao bì, vận chuyển)';
COMMENT ON COLUMN alerts.evidence IS 'Bằng chứng trích đoạn các review tiêu biểu của khách hàng';
COMMENT ON COLUMN alerts.status IS 'Trạng thái xử lý: alerted (mới báo) -> investigating (đang kiểm tra) -> resolved (đã xử lý) / false_alarm (báo nhầm)';
