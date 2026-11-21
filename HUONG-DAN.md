# Hướng dẫn khởi động & chỉnh sửa trên điện thoại

Tài liệu này dành cho người không chuyên. Làm tuần tự, mỗi bước đều có lệnh copy được.

---

## 0. Chọn đúng con đường

| Bạn muốn                           | Dùng cách                    | Cần chuẩn bị                        |
| ---------------------------------- | ---------------------------- | ----------------------------------- |
| Xem thử trên máy tính              | **Cách 1** — chạy local      | Máy tính + Python                   |
| Xem trên điện thoại trong nhà      | **Cách 2** — local + WiFi    | Điện thoại cùng WiFi                |
| Dùng mọi lúc, sửa bằng điện thoại  | **Cách 3** — GitHub + Render | Tài khoản GitHub, Render (miễn phí) |
| Chạy ngay trong điện thoại Android | **Cách 4** — Termux          | Android, không cần máy tính         |

> ⚠️ Địa chỉ `localhost:8000` chỉ có nghĩa **trên chính máy đang chạy server**. Điện thoại mở `localhost` là mở chính nó, không phải site của bạn. Muốn xem trên điện thoại: dùng Cách 2 (cùng WiFi) hoặc Cách 3 (đưa lên Internet).



---

## 1. Cách 1 — Chạy trên máy tính

### Windows

1. Tải Python 3.11 tại <https://python.org/downloads> — khi cài **tích "Add python.exe to PATH"**.
2. Mở **PowerShell** (phím Windows → gõ `powershell`).
3. Di chuyển vào thư mục dự án:


   ```powershell
   cd C:\duong\dan\sotayluadao
   ```
4. Cài thư viện (chỉ lần đầu):
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Chạy:
   ```powershell
   python -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```
6. Mở Chrome → `http://localhost:8000`. Dừng server: bấm `Ctrl + C` trong PowerShell.

### macOS / Linux

```bash
cd /duong/dan/sotayluadao
./run.sh
```

`run.sh` tự cài thư viện, tự in ra địa chỉ máy tính **và** địa chỉ để điện thoại truy cập.

Lần chạy đầu tiên sẽ tự tạo file `sotayluadao.db` và nạp 22 báo cáo mẫu.

---

## 2. Cách 2 — Mở trên điện thoại cùng WiFi

1. Chạy server với `--host 0.0.0.0` (lệnh ở Cách 1 đã có, hoặc dùng `run.sh`).
2. `run.sh` in ra dòng `Điện thoại (cùng WiFi): http://192.168.x.x:8000`. Nếu không dùng `run.sh`, lấy IP:
   - Windows: `ipconfig` → dòng **IPv4 Address**  
     |  |  |  
     | --- | --- |
   - macOS/Linux: `ifconfig | grep "inet "`
3. Trên điện thoại: kết nối **cùng một WiFi**, mở Chrome/Safari, gõ `http://192.168.x.x:8000`.

**Không vào được?**

- Windows lần đầu sẽ hiện hộp thoại Firewall → chọn **Allow access** cho Python.
- Điện thoại đang dùng 4G thay vì WiFi → tắt 4G, bật WiFi.
- WiFi công cộng/khách sạn thường chặn thiết bị nói chuyện với nhau → dùng Cách 3.

> Chỉ dùng trong nhà. Đừng mở cổng ra Internet bằng cách NAT port — không có HTTPS và không có bảo vệ gì.

---

## 3. Cách 3 — Đưa lên Internet (khuyến nghị, dùng được trên điện thoại mọi lúc)

### Bước 1 — Đưa code lên GitHub

1. Tạo tài khoản tại <https://github.com> (miễn phí).
2. Bấm **New repository** → đặt tên `sotayluadao` → chọn **Private** → **Create**.
3. Trên trang repo mới: **uploading an existing file** → kéo **toàn bộ nội dung** thư mục `sotayluadao` vào (không cần file `sotayluadao.db`) → **Commit changes**.

> Có Git trên máy thì nhanh hơn:
>
> ```bash
> git init && git add . && git commit -m "init"
> git remote add origin https://github.com/<tên-bạn>/sotayluadao.git
> git branch -M main && git push -u origin main
> ```

### Bước 2 — Deploy bằng Render

1. Vào <https://render.com> → **Sign in with GitHub**.
2. **New +** → **Blueprint** → chọn repo `sotayluadao` (Render tự đọc file `render.yaml`).  
   Không thấy Blueprint thì chọn **Web Service** → **Runtime: Docker**.
3. Ở phần Environment, nhập `STLL_ADMIN_KEY` = một chuỗi bí mật của bạn (ví dụ `stll-2026-bimat`). Đây là mật khẩu vào trang kiểm duyệt.
4. Bấm **Apply / Create** → chờ 2–3 phút.
5. Nhận địa chỉ dạng `https://sotayluadao-xxxx.onrender.com` → mở trên điện thoại.
6. Trên Chrome điện thoại: menu ⋮ → **Thêm vào Màn hình chính** để dùng như app.

**Lưu ý gói miễn phí của Render:**

- Site "ngủ" sau ~15 phút không có truy cập; lần vào đầu tiên chậm khoảng 30 giây.
- Ổ đĩa là tạm: **mỗi lần deploy lại, dữ liệu báo cáo sẽ về dữ liệu mẫu**. Dùng thật thì cần gắn PostgreSQL hoặc ổ đĩa trả phí.

### Bước 3 (tuỳ chọn) — Gắn tên miền riêng

Render → service → **Settings → Custom Domains → Add** → nhập tên miền bạn đã mua → làm theo hướng dẫn trỏ CNAME tại nhà cung cấp tên miền. HTTPS tự động sau vài phút.

---

## 4. Cách 4 — Chạy ngay trong điện thoại Android (Termux)

1. Cài **Termux** từ F-Droid (bản trên Google Play đã lỗi thời).
2. Mở Termux, gõ từng dòng:
   ```bash
   pkg update -y && pkg install -y python git
   git clone https://github.com/<tên-bạn>/sotayluadao.git
   cd sotayluadao
   pip install fastapi "uvicorn[standard]"
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```
3. Mở Chrome → `http://127.0.0.1:8000`.
4. Giữ Termux chạy nền: kéo thanh thông báo → **Acquire wakelock**.
5. Sửa file ngay trên máy: `nano static/index.html` (Ctrl+O để lưu, Ctrl+X để thoát).

**iPhone/iPad:** không có Termux. Dùng Cách 3 (sửa code bằng trình duyệt), hoặc GitHub **Codespaces** — có terminal chạy được trên Safari mobile.

---

## 5. Sửa gì thì vào đâu

| Muốn đổi                             | File                             | Vị trí                                             |
| ------------------------------------ | -------------------------------- | -------------------------------------------------- |
| Tên thương hiệu trên tab trình duyệt | `index.html`              | dòng 6 `<title>`                                   |
| Tên + khẩu hiệu ở header             | `index.html`              | dòng 22 `.brand-text`                              |
| Tiêu đề lớn + mô tả ở hero           | `index.html`              | dòng 40–45                                         |
| 4 thẻ cẩm nang                       | `index.html`              | từ dòng 131 `#cam-nang`                            |
| Disclaimer pháp lý ở footer          | `index.html`              | dòng 190 `.footer-legal` (khối chữ nhỏ cuối trang) |
| Màu chủ đạo (xanh mint)              | `style.css`               | dòng 9 `--mint`                                    |
| Màu nền tối                          | `style.css`               | dòng 2 `--navy`                                    |
| Màu cảnh báo/nguy hiểm               | `style.css`               | dòng 11 `--danger`                                 |
| Dữ liệu báo cáo mẫu                  | `app.py`                         | dòng 108 `SEED = [`                                |
| Ngưỡng mức rủi ro                    | `app.py`                         | dòng 33 `RISK_LEVELS`                              |
| Mật khẩu trang quản trị              | biến môi trường `STLL_ADMIN_KEY` | không sửa code                                     |
| Tên miền/SEO                         | `index.html`              | thẻ `<meta name="description">` dòng 7             |

Ví dụ đổi tên thương hiệu — sửa **3 chỗ** trong `index.html`:

```html
<title>Sổ Tay Lừa Đảo — ...</title>          
<strong>Sổ Tay Lừa Đảo</strong>              
<strong>Sổ Tay Lừa Đảo</strong>              
```

---

## 6. Đổi dữ liệu mẫu

Dữ liệu mẫu chỉ được nạp **khi database còn trống**.

1. Sửa danh sách `SEED` trong `app.py` (dòng 108), mỗi dòng theo thứ tự:  
   `(đối tượng, loại, tiêu đề, diễn biến, thiệt hại, kênh, người gửi)`  
   Loại hợp lệ: `phone`, `bank`, `web`, `social`.
2. Xoá file `sotayluadao.db`.
3. Chạy lại server → dữ liệu mới được nạp.

**Cách khác không cần sửa code:** vào `/admin` trên điện thoại, gửi báo cáo qua nút "Gửi báo cáo" rồi duyệt. Đây cũng là cách bạn nhập dữ liệu thật.

---

## 7. Sửa code bằng điện thoại (không cần máy tính)

1. Mở `github.com` bằng Chrome/Safari, đăng nhập.
2. Vào repo → `static` → chạm `index.html`.
3. Chạm biểu tượng **bút chì ✏️** (góc phải).
4. Sửa trực tiếp → kéo xuống → **Commit changes** → **Commit changes**.
5. Nếu đã deploy bằng Render: chờ ~1 phút, Render tự build lại. Mở lại link trên điện thoại.

**Sửa CSS/JS mà không thấy thay đổi?** Trình duyệt điện thoại cache rất lì. Mở **tab ẩn danh**, hoặc đổi đường dẫn trong `index.html` thành `/static/style.css?v=2` rồi tăng số mỗi lần sửa.

**Sửa nhiều file cùng lúc:** dùng **github.dev** — trên trang repo bấm phím `.` (hoặc đổi `github.com` thành `github.dev` trong địa chỉ) để có trình soạn thảo đầy đủ ngay trong trình duyệt điện thoại.

---

## 8. Kiểm duyệt báo cáo trên điện thoại

1. Mở `https://<site-của-bạn>/admin`.
2. Nhập khoá `STLL_ADMIN_KEY` (mặc định khi chạy local: `demo-admin`).
3. Bấm **Duyệt** hoặc **Từ chối** cho từng báo cáo.

Khoá được lưu trong máy nên lần sau không phải nhập lại. Nếu quên khoá: vào Render → Environment → xem/sửa `STLL_ADMIN_KEY`.

---

## 9. Lỗi thường gặp

| Hiện tượng                            | Nguyên nhân                    | Cách xử lý                                          |
| ------------------------------------- | ------------------------------ | --------------------------------------------------- |
| `Address already in use`              | Cổng 8000 đang bận             | Đổi `--port 8001`, mở `localhost:8001`              |
| `ModuleNotFoundError: fastapi`        | Chưa cài thư viện              | Chạy `pip install -r requirements.txt`              |
| Điện thoại không mở được `192.168...` | Khác WiFi / firewall           | Cùng WiFi; Allow Python ở firewall                  |
| Sửa `SEED` mà dữ liệu không đổi       | Database cũ còn đó             | Xoá `sotayluadao.db`, chạy lại                      |
| `/admin` báo `Sai khoá quản trị`      | Sai `STLL_ADMIN_KEY`           | Nhập đúng khoá, hoặc xoá localStorage               |
| Deploy xong nhưng trang trắng/502     | Build lỗi hoặc sai cổng        | Render → **Logs**; Dockerfile đã tự đọc biến `PORT` |
| Báo cáo mất sau khi deploy lại        | Ổ đĩa tạm của gói free         | Chấp nhận khi thử, hoặc gắn PostgreSQL              |
| Số liệu ở hero vẫn là 22              | Chưa có báo cáo mới được duyệt | Duyệt báo cáo ở `/admin` rồi tải lại                |

---

## 10. Nhắc lại một điều quan trọng

Khi gắn tên miền, chọn tên **không** na ná site tra cứu đang có (thêm/bớt ký tự). Ngoài rủi ro bị khiếu nại thương hiệu, các tổ chức chống lừa đảo và trình duyệt duy trì danh sách đen các tên miền giả mạo — site sẽ bị chặn ngay khi có người dùng đầu tiên. Các lựa chọn an toàn: `tracuuluadao.vn`, `canhbaolua.vn`, `socthaylua.com`.
