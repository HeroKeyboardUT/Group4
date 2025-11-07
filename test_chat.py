"""
Script tự động để test hệ thống chat P2P
Chạy script này để khởi động tất cả các thành phần cần thiết
"""

import subprocess
import time
import sys
import os

def start_server():
    """Khởi động central server"""
    print("=" * 60)
    print("Đang khởi động Central Server...")
    print("=" * 60)
    
    server_process = subprocess.Popen([
        sys.executable, 
        'chat_server.py',
        '--server-ip', '127.0.0.1',
        '--server-port', '8000'
    ])
    
    time.sleep(2)  # Đợi server khởi động
    return server_process

def start_peer(username, port):
    """Khởi động một peer"""
    print("\nĐang khởi động peer: {} (port {})...".format(username, port))
    
    peer_process = subprocess.Popen([
        sys.executable,
        'chat_peer.py',
        '--username', username,
        '--peer-port', str(port),
        '--server-ip', '127.0.0.1',
        '--server-port', '8000'
    ])
    
    time.sleep(1)
    return peer_process

def main():
    """Main test function"""
    processes = []
    
    try:
        # Khởi động Central Server
        server = start_server()
        processes.append(server)
        
        # Khởi động các peers
        peers_config = [
            ('Alice', 5001),
            ('Bob', 5002),
            ('Charlie', 5003)
        ]
        
        for username, port in peers_config:
            peer = start_peer(username, port)
            processes.append(peer)
        
        print("\n" + "=" * 60)
        print("HỆ THỐNG ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
        print("=" * 60)
        print("\nCentral Server: http://127.0.0.1:8000")
        print("\nCác Peer đang chạy:")
        print("  - Alice:   http://127.0.0.1:5001")
        print("  - Bob:     http://127.0.0.1:5002")
        print("  - Charlie: http://127.0.0.1:5003")
        print("\n" + "=" * 60)
        print("Mở trình duyệt và truy cập:")
        print("  http://127.0.0.1:5001/chat.html")
        print("  http://127.0.0.1:5002/chat.html")
        print("  http://127.0.0.1:5003/chat.html")
        print("=" * 60)
        print("\nNhấn Ctrl+C để dừng tất cả các service...")
        
        # Giữ script chạy
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nĐang dừng tất cả services...")
        for process in processes:
            process.terminate()
        
        time.sleep(1)
        
        for process in processes:
            process.kill()
        
        print("Đã dừng tất cả services!")

if __name__ == "__main__":
    main()
