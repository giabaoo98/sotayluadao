#!/usr/bin/env bash
# Chạy site trên máy tính và in luôn địa chỉ để mở từ điện thoại cùng WiFi.
set -e
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt

PORT="${PORT:-8000}"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')

echo ""
echo "  Máy tính:            http://localhost:${PORT}"
[ -n "$IP" ] && echo "  Điện thoại (cùng WiFi): http://${IP}:${PORT}"
echo "  Trang kiểm duyệt:    http://localhost:${PORT}/admin"
echo ""

exec python3 -m uvicorn app:app --host 0.0.0.0 --port "${PORT}" --reload
