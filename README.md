# Sổ Tay Lừa Đảo

Website tra cứu – cảnh báo lừa đảo trực tuyến: tìm số điện thoại, số tài khoản ngân hàng,
website, tài khoản Facebook/TikTok đã từng bị cộng đồng báo cáo; gửi báo cáo mới và kiểm duyệt
trước khi công khai.

> Đây là sản phẩm **độc lập**, thương hiệu và giao diện gốc. Không phải bản sao của bất kỳ site
> tra cứu nào đang hoạt động.

> **Mới bắt đầu?** Đọc [`HUONG-DAN.md`](HUONG-DAN.md) — hướng dẫn từng bước khởi động, mở trên điện thoại,
> deploy lên Internet và sửa nội dung ngay trên điện thoại.

## Chạy thử

```bash
cd sotayluadao
./run.sh          # tự cài thư viện, in luôn địa chỉ LAN cho điện thoại
```

Hoặc thủ công:

```bash
pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Mở http://localhost:8000 — trang kiểm duyệt: http://localhost:8000/admin (khoá mặc định `demo-admin`,
đổi bằng biến môi trường `STLL_ADMIN_KEY`).

Tuỳ chọn:

| Biến môi trường | Mặc định | Ý nghĩa |
|---|---|---|
| `STLL_DB` | `sotayluadao.db` | Đường dẫn file SQLite |
| `STLL_ADMIN_KEY` | `demo-admin` | Khoá cho API kiểm duyệt |

## Cấu trúc

```
sotayluadao/
├── app.py              # FastAPI: API tra cứu, báo cáo, kiểm duyệt + phục vụ file tĩnh
├── sotayluadao.db      # SQLite (tự tạo & seed lần chạy đầu)
├── index.html          # Trang chủ: hero, ô tra cứu, kết quả, cảnh báo, cẩm nang
├── admin.html          # Hàng chờ kiểm duyệt
├── style.css           # Design system (token màu, component)
├── app.js              # Gọi API, render kết quả, form báo cáo
├── robots.txt
├── requirements.txt    # fastapi, uvicorn
├── Dockerfile          # build image, tự đọc biến PORT
├── render.yaml         # deploy 1 click trên Render
├── run.sh              # chạy local + in địa chỉ LAN cho điện thoại
└── HUONG-DAN.md        # hướng dẫn từng bước
```

> Cấu trúc **phẳng** (không có thư mục con) là cố ý: trên điện thoại bạn chỉ cần chọn tất cả file
> và upload một lần lên GitHub, không phải kéo-thả thư mục.

## API

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/search?q=&type=` | Tra cứu, gộp kết quả theo đối tượng + mức rủi ro |
| GET | `/api/stats` | Tổng báo cáo, số đối tượng, tổng thiệt hại |
| GET | `/api/top?limit=` | Đối tượng bị báo cáo nhiều nhất |
| GET | `/api/recent?limit=` | Báo cáo mới nhất |
| POST | `/api/reports` | Gửi báo cáo (vào hàng chờ duyệt) |
| GET | `/api/admin/pending?key=` | Danh sách chờ duyệt |
| POST | `/api/admin/approve/{id}?key=&action=` | Duyệt / từ chối |

Mức rủi ro: `0 báo cáo` → chưa có dữ liệu · `1` → cần thận trọng · `2–4` → cảnh báo · `≥5` → nguy hiểm cao.

## Giao diện

Thiết kế responsive, đã kiểm tra ở **390px (điện thoại)**, **768px (tablet)** và **1440px (máy tính)**,
không có cuộn ngang ở bất kỳ kích thước nào:

- Điện thoại: menu hamburger, ô tìm kiếm full-width, thẻ thống kê 2 cột, bảng báo cáo chuyển thành
  danh sách thẻ có nhãn, form báo cáo dạng bottom sheet, ô nhập 16px để iOS không tự zoom.
- Máy tính: menu ngang, lưới 3 cột cho cảnh báo, 4 cột cho cẩm nang, khổ nội dung 1200px.
- Chi tiết: `viewport-fit=cover` cho tai thỏ, `theme-color`, hỗ trợ "Thêm vào màn hình chính",
  tôn trọng `prefers-reduced-motion`, không dính hiệu ứng hover trên thiết bị cảm ứng.

## Dữ liệu

Toàn bộ dữ liệu seed trong `app.py` là **dữ liệu minh hoạ**: số điện thoại/STK dạng `0900 000 117`,
`7777 0000 1111`, tên miền `.example`. Không trỏ tới cá nhân hay tổ chức có thật — điều này quan trọng
vì gắn nhãn "lừa đảo" cho một người thật có thể cấu thành xâm phạm uy tín và bị kiện.

Trước khi chạy thật, cần:

1. Xoá dữ liệu seed, thay bằng báo cáo thật đã kiểm duyệt.
2. Quy trình kiểm duyệt: mọi báo cáo vào `pending`, chỉ `approved` mới hiển thị.
3. Cơ chế đính chính: người bị báo cáo có quyền yêu cầu gỡ/ phản hồi, hiển thị ý kiến hai chiều.
4. Lưu log IP/timestamp khi gửi báo cáo (phục vụ xử lý tranh chấp).
5. Disclaimer pháp lý rõ ràng ở footer (đã có sẵn mẫu trong `index.html`).

## Triển khai

- **VPS**: chạy uvicorn sau nginx, `--workers 2`, bật HTTPS (Let's Encrypt).
- **Docker**: có sẵn `Dockerfile` (tự đọc biến `PORT`). `docker build -t sotayluadao . && docker run -p 8000:8000 sotayluadao`.
- **Render**: đã có `render.yaml` — chọn Blueprint, chỉ cần nhập `STLL_ADMIN_KEY`.
- **Quy mô lớn**: chuyển sang PostgreSQL (đổi lớp `db()`), thêm Redis cache cho `/api/top`,
  full-text index cho cột `norm`.
- Nên bật rate-limit cho `/api/search` và `/api/reports` (chống spam báo cáo).

## Gợi ý tên miền

`tracuuluadao.vn` · `canhbaolua.vn` · `socthaylua.com` · `kiemchungkhop.com` · `antoanthongtin.vn`

Tránh đăng ký tên miền na ná site đang hoạt động (thêm/bớt ký tự) — dễ bị khiếu nại thương hiệu
và bị đánh dấu là site giả mạo.
