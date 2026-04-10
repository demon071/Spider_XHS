# 🚀 Hướng dẫn Deploy & Cập nhật trên Oracle VPS

## Tổng quan kiến trúc

```
[Máy local] --git push--> [GitHub] --git pull--> [Oracle VPS]
                                                      |
                                               Docker Compose
                                                      |
                                          FastAPI server :5000
```

## Cấu trúc project

```
Spider_XHS/
├── server.py            # FastAPI server — endpoint chính /generate_params
├── Dockerfile           # Build image: Python + Node.js + npm install
├── docker-compose.yml   # Chạy container, expose port 5000
├── requirements.txt     # Python dependencies (fastapi, uvicorn, execjs, ...)
├── package.json         # Node dependencies (crypto-js, jsdom)
├── apis/
│   └── xhs_pc_apis.py   # Toàn bộ XHS API methods
├── xhs_utils/
│   └── xhs_util.py      # generate_request_params() — hàm ký request
└── static/
    ├── xhs_xs_xsc_56.js # JS dùng để sinh x-s, x-t, x-s-common
    └── xhs_xray.js      # JS dùng để sinh xray-traceid
```

---

## Lần đầu deploy lên VPS

```bash
# 1. SSH vào VPS
ssh ubuntu@<IP_VPS>

# 2. Clone repo
git clone https://github.com/demon071/Spider_XHS.git
cd Spider_XHS

# 3. Mở port firewall (chỉ cần làm 1 lần)
sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
sudo netfilter-persistent save
# Hoặc nếu dùng ufw:
# sudo ufw allow 5000/tcp

# 4. Build và chạy
docker compose up -d --build

# 5. Kiểm tra
docker compose ps
docker compose logs -f
```

> ⚠️ **Oracle VPS có 2 tầng firewall:**  
> Ngoài lệnh iptables trên VPS, phải vào **Oracle Cloud Console → Networking → VCN → Security Lists → Ingress Rules** và thêm rule cho TCP port 5000.

---

## Cập nhật code (workflow thông thường)

### Bước 1 — Sửa code trên máy local, push lên GitHub

```bash
git add .
git commit -m "mô tả thay đổi"
git push
```

### Bước 2 — Kéo code mới và rebuild trên VPS

```bash
ssh ubuntu@<IP_VPS>
cd Spider_XHS
git pull
docker compose up -d --build
```

---

## API — Endpoint duy nhất

### `POST /generate_params`

Gọi hàm `generate_request_params(cookies_str, api, data, method)` trong `xhs_util.py` và trả về headers + cookies + data đã được ký.

**Request Body:**

| Field | Type | Bắt buộc | Mô tả |
|-------|------|-----------|-------|
| `cookies_str` | string | ✅ | Cookie string đầy đủ lấy từ trình duyệt |
| `api` | string | ✅ | Path + query string, ví dụ `/api/sns/web/v1/user/otherinfo?target_user_id=abc` |
| `data` | any | ❌ | Body dict (POST) hoặc `""` (GET). Mặc định `""` |
| `method` | string | ❌ | `"POST"` hoặc `"GET"`. Mặc định `"POST"` |

**Ví dụ:**

```bash
curl -X POST "http://<IP_VPS>:5000/generate_params" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies_str": "a1=xxx; web_session=yyy; ...",
    "api": "/api/sns/web/v1/user/otherinfo?target_user_id=abc123",
    "data": "",
    "method": "GET"
  }'
```

**Response:**

```json
{
  "success": true,
  "headers": {
    "x-s": "...",
    "x-t": "...",
    "x-s-common": "...",
    "x-b3-traceid": "...",
    "x-xray-traceid": "...",
    "user-agent": "...",
    "...": "..."
  },
  "cookies": {
    "a1": "...",
    "web_session": "...",
    "...": "..."
  },
  "data": ""
}
```

**Swagger UI:** `http://<IP_VPS>:5000/docs`

---

## Các lệnh Docker thường dùng

```bash
# Xem log realtime
docker compose logs -f

# Xem container đang chạy
docker compose ps

# Dừng server
docker compose stop

# Khởi động lại (không rebuild)
docker compose start

# Dừng và xóa container
docker compose down

# Rebuild hoàn toàn (sau khi đổi Dockerfile hoặc package.json)
docker compose up -d --build --force-recreate
```

---

## Troubleshooting

### Lỗi `Cannot find module 'crypto-js'`
Node package chưa được cài. Kiểm tra Dockerfile có dòng `RUN npm install --omit=dev` sau khi `COPY package.json`.  
Rebuild: `docker compose up -d --build`

### Lỗi `KeyError: 'a1'`
`cookies_str` thiếu trường `a1`. Hãy lấy lại cookie đầy đủ từ trình duyệt tại `xiaohongshu.com`.

### Server không truy cập được từ ngoài
- Kiểm tra Oracle Security List đã mở port 5000 chưa (Console → Networking → VCN → Security Lists)
- Kiểm tra iptables: `sudo iptables -L INPUT | grep 5000`
- Kiểm tra container đang chạy: `docker compose ps`
