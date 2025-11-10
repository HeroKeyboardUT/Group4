# HƯỚNG DẪN DEMO HỆ THỐNG - COMPUTER NETWORKS

## 📋 Overview

Dự án bao gồm 2 tasks chính:
- **TASK 1**: Cookie-Based Authentication (Backend Server - Port 9000)
- **TASK 2**: Hybrid P2P Chat System (Chat Server + Peers)

---

## 🎯 TASK 1: Cookie-Based Authentication

### Mô tả
- Server xác thực user bằng cookie
- Login: POST /login với username=admin, password=password
- Access control: Kiểm tra cookie auth=true trước khi cho phép truy cập /

### Demo TASK 1

#### Bước 1: Khởi động Backend Server

```bash
python start_backend.py --server-ip 127.0.0.1 --server-port 9000
```

**Output:**
```
Link: http://127.0.0.1:9000
[Backend] Listening on port 9000
```

#### Bước 2: Test Task 1A - Login với Cookie

1. Mở browser: **http://127.0.0.1:9000/login.html**
2. Login:
   - Username: `admin`
   - Password: `password`
3. Mở DevTools (F12) → Tab **Application** → **Cookies**
4. ✅ Thấy cookie: `auth = true`

#### Bước 3: Test Task 1B - Access Control

**Test 1: Không có cookie → 401**
1. Mở **Incognito window** (Ctrl+Shift+N)
2. Truy cập: **http://127.0.0.1:9000/**
3. ✅ Kết quả: Hiển thị **401 Unauthorized**

**Test 2: Có cookie → 200 OK**
1. Sau khi login, truy cập: **http://127.0.0.1:9000/**
2. ✅ Kết quả: Hiển thị **index.html**

**Test 3: Xóa cookie → 401**
1. DevTools → Application → Cookies → Delete `auth`
2. Refresh trang (F5)
3. ✅ Kết quả: Bị chặn với **401 Unauthorized**

#### Dừng Task 1
```
Ctrl + C trong terminal
```

---

## 🎯 TASK 2: Hybrid P2P Chat System

### Mô tả
- Hybrid architecture: Client-Server (initialization) + P2P (messaging)
- Direct messaging, broadcast, channel communication
- Real-time với long polling (< 1s latency)
- Handshake protocol trước khi chat

### Demo TASK 2

#### Bước 1: Khởi động toàn bộ hệ thống (1 lệnh)

```bash
python test_chat.py
```

**Output:**
```
============================================================
Đang khởi động Central Server...
============================================================
Đang khởi động peer: Alice (port 5001)...
Đang khởi động peer: Bob (port 5002)...
Đang khởi động peer: Charlie (port 5003)...
============================================================
HỆ THỐNG ĐÃ KHỞI ĐỘNG THÀNH CÔNG!
============================================================
```

#### Bước 2: Truy cập giao diện chat

Mở **3 tab** trình duyệt:
- **Alice**: http://127.0.0.1:5001
- **Bob**: http://127.0.0.1:5002
- **Charlie**: http://127.0.0.1:5003

**Lưu ý:** Không cần login, username đã được set qua command line

#### Bước 3: Demo Peer Discovery

1. Click **Refresh** trong phần "Online Peers"
2. ✅ Thấy 3 peers: `peer_5001, peer_5002, peer_5003`

#### Bước 4: Demo Handshake (Bắt buộc!)

**Tại tab Alice:**
1. Peer ID: `peer_5002`
2. Click **Handshake**
3. ✅ Thông báo: "Handshake successful with Bob"

**Lặp lại:** Alice handshake với Charlie (`peer_5003`)

#### Bước 5: Demo Direct Message (P2P)

**Tại tab Alice:**
1. Direct To: `peer_5002`
2. Message: `Hello Bob!`
3. Click **Send**

**Tại tab Bob:**
✅ Tin nhắn hiển thị ngay lập tức: `[direct] peer_5001 -> me: Hello Bob!`

#### Bước 6: Demo Broadcast

**Tại tab Alice:**
1. Broadcast Message: `Meeting at 3PM`
2. Click **Broadcast**

**Tại tab Bob và Charlie:**
✅ Cả 2 nhận tin đồng thời: `[broadcast] peer_5001: Meeting at 3PM`

#### Bước 7: Demo Channel Communication

**Bước 7.1: Tạo channel (Alice)**
1. Channel Name: `project-x`
2. Click **+ Create Channel**

**Bước 7.2: Join channel (Bob & Charlie)**
1. Click **Refresh** trong phần Channels
2. Click **Join** bên cạnh `project-x`

**Bước 7.3: Gửi tin vào channel (Alice)**
1. Channel: `project-x`
2. Message: `Sprint planning today`
3. Click **Send**

**Kết quả:**
✅ Bob và Charlie nhận tin (không cần handshake trước!)

#### Bước 8: Demo Real-time Update

1. Mở DevTools (F12) → Tab **Network**
2. Tìm request: `/api/messages/poll`
3. ✅ Thấy status: **pending** (long polling đang chờ)
4. Khi có tin mới → request return ngay lập tức
5. ✅ Độ trễ: **< 1 giây**

#### Dừng Task 2
```
Ctrl + C trong terminal (dừng tất cả services)
```

---

## 📝 Checklist Demo 

### ✅ TASK 1 Demo Checklist

- [ ] Khởi động backend server (port 9000)
- [ ] Mở browser: http://127.0.0.1:9000/login.html
- [ ] Login với admin/password
- [ ] F12 → Application → Cookies → Thấy `auth=true`
- [ ] Mở Incognito → Truy cập / → Thấy 401
- [ ] Tab đã login → Truy cập / → Thấy index.html
- [ ] Xóa cookie → Refresh → Thấy 401

### ✅ TASK 2 Demo Checklist

- [ ] Chạy `python test_chat.py`
- [ ] Mở 3 tab: 5001, 5002, 5003
- [ ] Click Refresh → Thấy 3 peers online
- [ ] Alice handshake với Bob
- [ ] Alice gửi direct message cho Bob
- [ ] Bob thấy tin nhắn ngay lập tức
- [ ] Alice broadcast → Bob & Charlie nhận tin
- [ ] Alice tạo channel `project-x`
- [ ] Bob & Charlie join channel
- [ ] Alice gửi tin vào channel
- [ ] Tất cả members nhận tin
- [ ] F12 → Network → Thấy long polling `/api/messages/poll`

---

## 🎬 Script Demo Nhanh (5 phút)

### Minute 1-2: TASK 1
```
1. Khởi động backend
2. Login → Show cookie
3. Incognito → Show 401
4. Xóa cookie → Show 401
```

### Minute 3-5: TASK 2
```
1. Chạy test_chat.py
2. Mở 3 tabs
3. Handshake + Direct message
4. Broadcast
5. Channel communication
6. Show long polling
```

---

## 🔧 Khởi Động Thủ Công (Nếu Cần)

### TASK 1: Backend Server

```bash
python start_backend.py --server-ip 127.0.0.1 --server-port 9000
```

### TASK 2: Chat System (4 terminal riêng biệt)

**Terminal 1 - Central Server:**
```bash
python chat_server.py --server-ip 127.0.0.1 --server-port 8000
```

**Terminal 2 - Alice:**
```bash
python chat_peer.py --username Alice --peer-port 5001 --server-ip 127.0.0.1
```

**Terminal 3 - Bob:**
```bash
python chat_peer.py --username Bob --peer-port 5002 --server-ip 127.0.0.1
```

**Terminal 4 - Charlie:**
```bash
python chat_peer.py --username Charlie --peer-port 5003 --server-ip 127.0.0.1
```

---

## ⚠️ Lưu Ý Quan Trọng

### TASK 1 vs TASK 2

| Feature | TASK 1 (Backend) | TASK 2 (Chat) |
|---------|------------------|---------------|
| Port | 9000 | 8000, 5001-5003 |
| Authentication | ✅ Cookie required | ❌ No login needed |
| URL | /login.html, / | /chat.html |

### Handshake trong Chat

- **Bắt buộc** cho Direct Message và Broadcast
- **Không cần** cho Channel messages
- Handshake 1 lần cho mỗi cặp peer

### Real-time Update

- Sử dụng **Long Polling** (không phải WebSocket)
- Độ trễ < 1 giây
- Giảm 82.5% network overhead vs short polling

---

## ❌ Troubleshooting

**Lỗi: Port already in use**
```
→ Ctrl+C dừng tất cả processes Python
→ Hoặc đổi port
```

**Lỗi: Connection refused**
```
→ Kiểm tra server đã chạy chưa
→ Đợi 2-3 giây sau khi start
```

**Handshake required**
```
→ Phải handshake trước khi gửi direct/broadcast
→ Nhập đúng peer ID: peer_5002 (không phải 5002)
```

**TASK 1 yêu cầu login khi test TASK 2**
```
→ TASK 1 (port 9000) và TASK 2 (port 5001-5003, 8000) chạy riêng biệt
→ Đảm bảo truy cập đúng port cho mỗi task
```

---

## 📊 Architecture Summary

```
TASK 1 (Cookie Auth):
Browser → Backend (9000) → Check Cookie → Serve/Deny

TASK 2 (Hybrid Chat):
Initialization: Peer → Chat Server (8000) → Registration
Messaging: Peer A ⟷ Peer B (P2P Direct, port+1000)
```

---

## 🎓 Assignment Requirements Met

✅ Task 1A: Login authentication with cookie
✅ Task 1B: Cookie-based access control
✅ Task 2: Peer registration & discovery
✅ Task 2: Direct P2P messaging
✅ Task 2: Broadcast messaging
✅ Task 2: Channel management
✅ Task 2: Real-time notifications
✅ All 7 required APIs implemented
✅ Concurrency with threading
✅ Error handling
