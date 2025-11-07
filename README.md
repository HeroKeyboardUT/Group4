# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG CHAT P2P

## 📋 Mô Tả

Hệ thống chat P2P cho phép người dùng:

- Gửi tin nhắn trực tiếp (Direct Message)
- Broadcast tin nhắn tới tất cả peers
- Tạo và tham gia các channel
- Giao tiếp real-time không cần refresh trang

## 🚀 Cách Chạy Hệ Thống

### Phương Án 1: Sử Dụng Script Tự Động (Khuyến Nghị)

#### Windows:

```batch
start_chat_system.bat
```

#### Linux/Mac:

```bash
python test_chat.py
```

Script sẽ tự động khởi động:

- Central Server (port 8000)
- 3 peers: Alice (5001), Bob (5002), Charlie (5003)

### Phương Án 2: Khởi Động Thủ Công

#### Bước 1: Khởi động Central Server

Mở terminal mới:

```bash
python chat_server.py --server-ip 127.0.0.1 --server-port 8000
```

#### Bước 2: Khởi động Peer Alice

Mở terminal mới:

```bash
python chat_peer.py --username Alice --peer-port 5001 --server-ip 127.0.0.1
```

#### Bước 3: Khởi động Peer Bob

Mở terminal mới:

```bash
python chat_peer.py --username Bob --peer-port 5002 --server-ip 127.0.0.1
```

#### Bước 4: Khởi động Peer Charlie

Mở terminal mới:

```bash
python chat_peer.py --username Charlie --peer-port 5003 --server-ip 127.0.0.1
```

## 🌐 Truy Cập Giao Diện Web

Sau khi khởi động, mở trình duyệt và truy cập:

- **Alice**: http://127.0.0.1:5001
- **Bob**: http://127.0.0.1:5002
- **Charlie**: http://127.0.0.1:5003

## 📱 Hướng Dẫn Sử Dụng Giao Diện

### 1. Xem Danh Sách Peers Online

- Phần "Online Peers" hiển thị tất cả peers đang online
- Click nút "↻" để refresh danh sách

### 2. Gửi Tin Nhắn Trực Tiếp (Direct Message)

1. Nhập ID của peer muốn gửi (vd: `peer_5002`)
2. Nhập nội dung tin nhắn
3. Click "Send"

**Ví dụ:**

- Alice muốn gửi tin cho Bob:
  - Direct To: `peer_5002`
  - Message: `Xin chào Bob!`

### 3. Broadcast Tin Nhắn

1. Nhập tin nhắn vào ô "Broadcast"
2. Click "Broadcast"
3. Tất cả peers sẽ nhận được tin nhắn

### 4. Tạo Channel

1. Nhập tên channel (vd: `team-a`)
2. Click nút "+"
3. Channel được tạo và bạn tự động join

### 5. Tham Gia Channel

1. Xem danh sách channels
2. Click "Join" bên cạnh channel muốn tham gia

### 6. Gửi Tin Nhắn Vào Channel

1. Nhập tên channel (vd: `team-a`)
2. Nhập tin nhắn
3. Click "Send"
4. Tất cả members trong channel sẽ nhận được

## 🧪 Kịch Bản Test

### Test 1: Direct Message

1. Mở Alice (http://127.0.0.1:5001/)
2. Mở Bob (http://127.0.0.1:5002/)
3. Từ Alice, gửi tin nhắn trực tiếp cho Bob:
   - Direct To: `peer_5002`
   - Message: `Hello Bob từ Alice!`
4. Kiểm tra Bob nhận được tin nhắn

### Test 2: Broadcast

1. Mở cả 3 peers trên 3 tab khác nhau
2. Từ Alice, gửi broadcast:
   - Message: `Thông báo cho tất cả!`
3. Kiểm tra Bob và Charlie đều nhận được

### Test 3: Channel Communication

1. Từ Alice, tạo channel:
   - Channel name: `project-x`
   - Click "+"
2. Từ Bob, join channel:
   - Click "Join" bên cạnh `project-x`
3. Từ Charlie, join channel:
   - Click "Join" bên cạnh `project-x`
4. Từ Alice, gửi tin vào channel:
   - Channel: `project-x`
   - Message: `Họp team lúc 3PM`
5. Kiểm tra Bob và Charlie nhận được tin

### Test 4: Real-time Update

1. Để các tab mở
2. Gửi tin nhắn từ bất kỳ peer nào
3. Kiểm tra các peer khác tự động cập nhật (không cần refresh)

## 🔧 Cấu Hình Nâng Cao

### Thêm Peer Mới

```bash
python chat_peer.py --username Dave --peer-port 5004 --server-ip 127.0.0.1
```

Sau đó truy cập: http://127.0.0.1:5004/

### Thay Đổi Server Port

```bash
python chat_server.py --server-ip 127.0.0.1 --server-port 9000
```

Khi chạy peers, chỉ định server port:

```bash
python chat_peer.py --username Alice --peer-port 5001 --server-ip 127.0.0.1 --server-port 9000
```

## ❌ Troubleshooting

### Lỗi: "Port already in use"

- Đóng tất cả terminal đang chạy
- Hoặc thay đổi port trong lệnh khởi động

### Lỗi: "Connection refused"

- Kiểm tra Central Server đã chạy chưa
- Kiểm tra IP và port có đúng không

### Peers không thấy nhau

- Đợi 2-3 giây sau khi khởi động
- Click nút refresh (↻) trong phần Online Peers

### Tin nhắn không được gửi

- Kiểm tra peer ID nhập đúng định dạng: `peer_XXXX`
- Kiểm tra peer đích có online không

## 📊 Kiến Trúc Hệ Thống
