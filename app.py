"""
Sổ Tay Lừa Đảo — backend tra cứu & báo cáo lừa đảo trực tuyến.
FastAPI + SQLite, chạy: uvicorn app:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.environ.get("STLL_DB", BASE_DIR / "sotayluadao.db"))
SERVED_FILES = {"index.html", "admin.html", "style.css", "app.js", "robots.txt"}

app = FastAPI(title="Sổ Tay Lừa Đảo API", docs_url="/api/docs", redoc_url=None)

TYPE_LABELS = {
    "phone": "SĐT / Zalo",
    "bank": "STK ngân hàng",
    "social": "Facebook / TikTok",
    "web": "Website",
    "other": "Khác",
}

RISK_LEVELS = [
    (5, "critical", "Nguy hiểm cao"),
    (2, "high", "Cảnh báo"),
    (1, "low", "Cần thận trọng"),
    (0, "none", "Chưa có báo cáo"),
]


# --------------------------------------------------------------------------- #
# DB
# --------------------------------------------------------------------------- #
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                norm TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                reason TEXT NOT NULL,
                amount INTEGER DEFAULT 0,
                channel TEXT,
                evidence TEXT,
                alias TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_norm ON reports(norm);
            CREATE INDEX IF NOT EXISTS idx_status ON reports(status);
            """
        )


def normalize(raw: str) -> str:
    s = (raw or "").strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"^www\.", "", s)
    s = re.sub(r"[\s.\-+()]", "", s)
    return s.rstrip("/")


def risk_of(count: int) -> dict:
    for threshold, key, label in RISK_LEVELS:
        if count >= threshold:
            return {"key": key, "label": label}
    return {"key": "none", "label": "Chưa có báo cáo"}


def row_to_report(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "target": row["target"],
        "type": row["type"],
        "type_label": TYPE_LABELS.get(row["type"], "Khác"),
        "title": row["title"],
        "reason": row["reason"],
        "amount": row["amount"],
        "channel": row["channel"],
        "evidence": row["evidence"],
        "alias": row["alias"],
        "created_at": row["created_at"],
    }


# --------------------------------------------------------------------------- #
# Seed — dữ liệu DEMO, không phải cá nhân/tổ chức có thật
# --------------------------------------------------------------------------- #
SEED = [
    ("0900 000 117", "phone", "Giả danh nhân viên giao hàng",
     "Gọi báo có đơn hàng bị hoàn, yêu cầu chuyển 150.000đ phí lưu kho rồi chặn số.",
     150000, "Zalo", "demo"),
    ("0900 000 117", "phone", "Chiêu 'xác nhận đơn Shopee'",
     "Gửi link lạ yêu cầu đăng nhập để hoàn tiền, sau đó lấy mã OTP.",
     0, "Zalo", "demo"),
    ("0900 000 117", "phone", "Đòi nợ sai người",
     "Liên tục gọi đòi nợ một người khác, không chịu kiểm tra lại thông tin.",
     0, "Điện thoại", "demo"),
    ("0911 000 248", "phone", "Môi giới việc làm online",
     "Tuyển 'cộng tác viên chốt đơn', đóng 500.000đ tiền cọc thì bị chặn liên lạc.",
     500000, "Zalo", "demo"),
    ("0988 000 305", "phone", "Giả danh công an, viện kiểm sát",
     "Yêu cầu cài app dịch vụ công giả để 'xác minh tài khoản', chiếm quyền điều khiển điện thoại.",
     0, "Điện thoại", "demo"),
    ("0988 000 305", "phone", "Cuộc gọi video chia sẻ màn hình",
     "Dẫn dụ chia sẻ màn hình để đọc mã OTP ngân hàng.",
     0, "Điện thoại", "demo"),
    ("7777 0000 1111", "bank", "STK nhận tiền hàng giả",
     "Nhận tiền cọc mua điện thoại nhưng không giao hàng, sau đó đổi thông tin liên hệ.",
     8000000, "Chuyển khoản", "demo"),
    ("7777 0000 1111", "bank", "Bán hàng online không giao",
     "Đặt cọc 30% qua STK này, người bán biến mất sau 3 ngày.",
     4500000, "Chuyển khoản", "demo"),
    ("7777 0000 1111", "bank", "Yêu cầu chuyển thêm 'phí xác minh'",
     "Sau khi chuyển đủ tiền, yêu cầu thêm phí xác minh 2.000.000đ để 'giải ngân'.",
     2000000, "Chuyển khoản", "demo"),
    ("7777 0000 1111", "bank", "Sai nội dung chuyển khoản",
     "Báo sai nội dung, yêu cầu chuyển lại lần hai vào cùng STK.",
     3000000, "Chuyển khoản", "demo"),
    ("6666 0000 2222", "bank", "STK của sàn đầu tư giả",
     "Nạp tiền vào app đầu tư 'lãi 8%/tuần', rút không được, nhân viên chặn liên lạc.",
     25000000, "Chuyển khoản", "demo"),
    ("6666 0000 2222", "bank", "Tuyển CTV nạp tiền đơn hàng",
     "Nạp tiền làm nhiệm vụ, đơn càng lớn càng không rút được.",
     12000000, "Chuyển khoản", "demo"),
    ("5555 0000 3333", "bank", "Trung gian đổi tiền",
     "Nhận tiền đổi ngoại tệ, không giao tiền, xoá tin nhắn.",
     15000000, "Chuyển khoản", "demo"),
    ("https://demo-shop-gia-re.example", "web", "Web bán hàng giả mạo thương hiệu",
     "Giao diện nhái trang chính hãng, giá rẻ bất thường, thanh toán chỉ nhận chuyển khoản cá nhân.",
     0, "Website", "demo"),
    ("https://demo-dautu-laixuat.example", "web", "App/web đầu tư lãi suất cao",
     "Hứa lãi cố định mỗi ngày, yêu cầu nạp thêm để 'mở khoá' lệnh rút.",
     30000000, "Website", "demo"),
    ("https://demo-vay-online.example", "web", "Vay tiền online giải ngân trước",
     "Thu phí hồ sơ trước khi giải ngân, không có hợp đồng, không có giấy phép.",
     1200000, "Website", "demo"),
    ("https://demo-lot-xac-hang-khong.example", "web", "Giả mạo hãng bay bán vé giá rẻ",
     "Tên miền thêm bớt ký tự so với hãng thật, nhận tiền qua tài khoản cá nhân.",
     6800000, "Website", "demo"),
    ("fb.com/demo.tiktok.scam.01", "social", "Page bán hàng 'xả kho'",
     "Chạy quảng cáo giá rẻ, nhận cọc rồi chặn tin nhắn.",
     990000, "Facebook", "demo"),
    ("fb.com/demo.tiktok.scam.01", "social", "Tài khoản giả danh người nổi tiếng",
     "Mạo danh để mời tham gia 'quỹ đầu tư', yêu cầu chuyển tiền vào STK cá nhân.",
     5000000, "Facebook", "demo"),
    ("fb.com/demo.tiktok.scam.02", "social", "TikTok bán mỹ phẩm không rõ nguồn gốc",
     "Nhận tiền, gửi hàng sai mô tả, không hỗ trợ đổi trả.",
     350000, "TikTok", "demo"),
    ("fb.com/demo.tiktok.scam.02", "social", "Nhóm 'việc làm tại nhà' thu phí",
     "Thu 200.000đ phí vào nhóm, sau đó không có việc.",
     200000, "Facebook", "demo"),
    ("0932 000 460", "phone", "Giả danh nhân viên điện lực cắt điện",
     "Đe doạ cắt điện, yêu cầu chuyển tiền 'thanh toán gấp' qua link lạ.",
     0, "Điện thoại", "demo"),
]


def seed_if_empty() -> None:
    with db() as conn:
        if conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]:
            return
        now = datetime.now()
        for i, (target, typ, title, reason, amount, channel, alias) in enumerate(SEED):
            created = (now - timedelta(days=i * 2 + 1, hours=i)).strftime("%Y-%m-%d %H:%M")
            conn.execute(
                """INSERT INTO reports (target, norm, type, title, reason, amount, channel, alias, status, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (target, normalize(target), typ, title, reason, amount, channel, alias, "approved", created),
            )
        # vài báo cáo đang chờ duyệt để demo luồng kiểm duyệt
        for target, typ, title, reason, amount, channel, alias in [
            ("0911 000 248", "phone", "Báo cáo mới: đòi cọc thêm",
             "Sau khi đóng cọc 500k, yêu cầu thêm 300k 'phí hệ thống'.", 300000, "Zalo", "demo"),
            ("https://demo-shop-gia-re.example", "web", "Báo cáo mới: web đổi tên miền",
             "Đổi sang tên miền khác nhưng vẫn cùng số STK nhận tiền.", 0, "Website", "demo"),
        ]:
            conn.execute(
                """INSERT INTO reports (target, norm, type, title, reason, amount, channel, alias, status, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (target, normalize(target), typ, title, reason, amount, channel, alias, "pending",
                 datetime.now().strftime("%Y-%m-%d %H:%M")),
            )


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class ReportIn(BaseModel):
    target: str = Field(min_length=4, max_length=200)
    type: str = "other"
    title: str = Field(min_length=6, max_length=120)
    reason: str = Field(min_length=20, max_length=2000)
    amount: int = 0
    channel: Optional[str] = ""
    evidence: Optional[str] = ""
    alias: Optional[str] = "Ẩn danh"


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
@app.get("/api/stats")
def stats():
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM reports WHERE status='approved'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM reports WHERE status='pending'").fetchone()[0]
        targets = conn.execute(
            "SELECT COUNT(DISTINCT norm) FROM reports WHERE status='approved'"
        ).fetchone()[0]
        by_type = {
            r["type"]: r["c"]
            for r in conn.execute(
                "SELECT type, COUNT(*) c FROM reports WHERE status='approved' GROUP BY type"
            )
        }
        lost = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM reports WHERE status='approved'"
        ).fetchone()[0]
    return {
        "total_reports": total,
        "total_targets": targets,
        "pending": pending,
        "by_type": by_type,
        "type_labels": TYPE_LABELS,
        "total_amount": lost,
    }


@app.get("/api/alerts")
def alerts():
    return {
        "items": [
            "Cẩn thận chiêu trò gọi video call chia sẻ màn hình để lấy mã OTP.",
            "Mọi giao dịch với lý do 'sai nội dung', 'xác minh', 'yêu cầu ngân hàng xác nhận thêm' đều là dấu hiệu lừa đảo.",
            "Không chuyển tiền cho tài khoản cá nhân khi mua hàng qua mạng xã hội.",
            "Tên miền giả mạo thường thêm/bớt ký tự — luôn kiểm tra kỹ thanh địa chỉ.",
            "Không cài ứng dụng ngoài kho chính thức khi được 'cán bộ' yêu cầu.",
        ]
    }


@app.get("/api/search")
def search(q: str = Query(min_length=2, max_length=200), type: str = "all"):
    n = normalize(q)
    like = f"%{n}%"
    sql = "SELECT * FROM reports WHERE status='approved' AND norm LIKE ?"
    params: list = [like]
    if type != "all":
        sql += " AND type = ?"
        params.append(type)
    sql += " ORDER BY created_at DESC"
    with db() as conn:
        rows = [row_to_report(r) for r in conn.execute(sql, params)]

    groups: dict[str, dict] = {}
    for r in rows:
        g = groups.setdefault(
            r["target"],
            {
                "target": r["target"],
                "type": r["type"],
                "type_label": r["type_label"],
                "report_count": 0,
                "total_amount": 0,
                "last_report": r["created_at"],
                "reports": [],
            },
        )
        g["report_count"] += 1
        g["total_amount"] += r["amount"]
        g["reports"].append(r)

    matches = []
    for g in groups.values():
        g["risk"] = risk_of(g["report_count"])
        matches.append(g)
    matches.sort(key=lambda x: (-x["report_count"], x["target"]))
    return {"query": q, "normalized": n, "type": type, "count": len(matches), "matches": matches}


@app.get("/api/recent")
def recent(limit: int = 12):
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE status='approved' ORDER BY created_at DESC LIMIT ?",
            (min(limit, 50),),
        )
        return {"items": [row_to_report(r) for r in rows]}


@app.get("/api/top")
def top(limit: int = 6):
    with db() as conn:
        rows = conn.execute(
            """SELECT target, type, COUNT(*) c, SUM(amount) amt, MAX(created_at) last
               FROM reports WHERE status='approved'
               GROUP BY norm ORDER BY c DESC, amt DESC LIMIT ?""",
            (min(limit, 20),),
        )
        out = []
        for r in rows:
            out.append(
                {
                    "target": r["target"],
                    "type": r["type"],
                    "type_label": TYPE_LABELS.get(r["type"], "Khác"),
                    "report_count": r["c"],
                    "total_amount": r["amt"],
                    "last_report": r["last"],
                    "risk": risk_of(r["c"]),
                }
            )
        return {"items": out}


@app.post("/api/reports")
def create_report(payload: ReportIn):
    if payload.type not in TYPE_LABELS:
        raise HTTPException(400, "Loại đối tượng không hợp lệ")
    n = normalize(payload.target)
    if len(n) < 4:
        raise HTTPException(400, "Thông tin cần tra cứu quá ngắn")
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO reports (target, norm, type, title, reason, amount, channel, evidence, alias, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                payload.target.strip(),
                n,
                payload.type,
                payload.title.strip(),
                payload.reason.strip(),
                max(0, int(payload.amount or 0)),
                (payload.channel or "").strip(),
                (payload.evidence or "").strip(),
                (payload.alias or "Ẩn danh").strip(),
                "pending",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
    return {
        "ok": True,
        "id": cur.lastrowid,
        "status": "pending",
        "message": "Báo cáo đã được ghi nhận và đang chờ kiểm duyệt.",
    }


@app.get("/api/admin/pending")
def admin_pending(key: str = ""):
    if key != os.environ.get("STLL_ADMIN_KEY", "demo-admin"):
        raise HTTPException(401, "Sai khoá quản trị")
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE status='pending' ORDER BY created_at DESC"
        )
        return {"items": [row_to_report(r) for r in rows]}


@app.post("/api/admin/approve/{rid}")
def admin_approve(rid: int, key: str = "", action: str = "approve"):
    if key != os.environ.get("STLL_ADMIN_KEY", "demo-admin"):
        raise HTTPException(401, "Sai khoá quản trị")
    new_status = "approved" if action == "approve" else "rejected"
    with db() as conn:
        conn.execute("UPDATE reports SET status=? WHERE id=?", (new_status, rid))
    return {"ok": True, "id": rid, "status": new_status}


# --------------------------------------------------------------------------- #
# Static
# --------------------------------------------------------------------------- #
@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html", headers={"Cache-Control": "no-cache"})


@app.get("/admin")
def admin_page():
    return FileResponse(BASE_DIR / "admin.html", headers={"Cache-Control": "no-cache"})


@app.get("/{filename}")
def flat_file(filename: str):
    """Phục vụ file tĩnh ở thư mục gốc — cấu trúc phẳng để upload từ điện thoại."""
    if filename in SERVED_FILES:
        # no-cache: sửa CSS/JS xong tải lại là thấy ngay, không bị trình duyệt giữ bản cũ
        return FileResponse(BASE_DIR / filename, headers={"Cache-Control": "no-cache"})
    raise HTTPException(404, "Not found")


@app.exception_handler(404)
def not_found(request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return FileResponse(BASE_DIR / "index.html")


init_db()
seed_if_empty()
