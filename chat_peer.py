#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
#

"""
chat_peer
~~~~~~~~~~~~~~~~~

P2P chat peer using WeApRous framework with form data.
Each peer runs as a web application with HTML UI.
"""

import socket
import threading
import argparse
from daemon.weaprous import WeApRous

# Peer configuration
peer_config = {
    'username': 'Anonymous',
    'peer_id': None,
    'peer_port': 5000,
    'server_ip': '127.0.0.1',
    'server_port': 8000,
    'connected_peers': {},
    'messages': [],
    'channels': {},
    'peer_list': []
}

app = WeApRous()

# P2P Socket Server
p2p_server_socket = None
p2p_running = False

def parse_form_data(body):
    """Parse form data: username=Alice&port=5001"""
    params = {}
    if not body or body == "anonymous":
        return params
    
    for pair in body.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            value = value.replace('+', ' ')
            params[key] = value
    return params

def build_form_data(data_dict):
    """Build form data from dictionary"""
    parts = []
    for key, value in data_dict.items():
        parts.append("{}={}".format(key, str(value).replace(' ', '+')))
    return "&".join(parts)

def send_http_to_server(method, path, form_data=None):
    """Send HTTP request with form data to central server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((peer_config['server_ip'], peer_config['server_port']))
        
        body = build_form_data(form_data) if form_data else ""
        request = "{} {} HTTP/1.1\r\n".format(method, path)
        request += "Host: {}:{}\r\n".format(
            peer_config['server_ip'], peer_config['server_port'])
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: {}\r\n".format(len(body))
        request += "\r\n{}".format(body)
        
        sock.sendall(request.encode())
        response = sock.recv(4096).decode()
        sock.close()
        
        if '\r\n\r\n' in response:
            body_part = response.split('\r\n\r\n', 1)[1]
            return parse_form_data(body_part)
        return None
    except Exception as e:
        print("[Peer] HTTP request error: {}".format(e))
        return None

def send_p2p_message(peer_ip, peer_port, message_data):
    """Send P2P message with form data."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((peer_ip, peer_port))
        
        body = build_form_data(message_data)
        request = "POST /p2p/message HTTP/1.1\r\n"
        request += "Host: {}:{}\r\n".format(peer_ip, peer_port)
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: {}\r\n".format(len(body))
        request += "\r\n{}".format(body)
        
        sock.sendall(request.encode())
        response = sock.recv(1024).decode()
        sock.close()
        return True
    except Exception as e:
        print("[Peer] P2P send error to {}:{}: {}".format(peer_ip, peer_port, e))
        return False

def handle_p2p_connection(conn, addr):
    """Handle incoming P2P connection."""
    try:
        request = conn.recv(2048).decode()
        
        if '\r\n\r\n' in request:
            body = request.split('\r\n\r\n', 1)[1]
            data = parse_form_data(body)
            
            msg_type = data.get('type', 'message')
            from_peer = data.get('from', 'unknown')
            content = data.get('message', '')
            channel = data.get('channel', '')
            
            # Store message
            peer_config['messages'].append({
                'from': from_peer,
                'to': 'me',
                'content': content,
                'type': msg_type,
                'channel': channel
            })
            
            print("[Peer] P2P message from {}: {}".format(from_peer, content))
            
            # Send success response
            response_body = build_form_data({'status': 'success'})
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: application/x-www-form-urlencoded\r\n"
            response += "Content-Length: {}\r\n".format(len(response_body))
            response += "\r\n{}".format(response_body)
            conn.sendall(response.encode())
    except Exception as e:
        print("[Peer] P2P handler error: {}".format(e))
        try:
            error_body = build_form_data({'status': 'error', 'message': str(e)})
            response = "HTTP/1.1 500 Internal Server Error\r\n"
            response += "Content-Type: application/x-www-form-urlencoded\r\n"
            response += "Content-Length: {}\r\n".format(len(error_body))
            response += "\r\n{}".format(error_body)
            conn.sendall(response.encode())
        except:
            pass
    finally:
        conn.close()

def start_p2p_listener():
    """Start P2P listener on separate thread."""
    global p2p_server_socket, p2p_running
    
    try:
        p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p2p_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        p2p_port = peer_config['peer_port'] + 1000
        p2p_server_socket.bind(('0.0.0.0', p2p_port))
        p2p_server_socket.listen(10)
        p2p_running = True
        
        print("[Peer] P2P listener started on port {}".format(p2p_port))
        
        while p2p_running:
            try:
                conn, addr = p2p_server_socket.accept()
                thread = threading.Thread(
                    target=handle_p2p_connection,
                    args=(conn, addr)
                )
                thread.daemon = True
                thread.start()
            except Exception as e:
                if p2p_running:
                    print("[Peer] Accept error: {}".format(e))
    except Exception as e:
        print("[Peer] P2P listener error: {}".format(e))
    finally:
        if p2p_server_socket:
            p2p_server_socket.close()

# ==================== WeApRous Routes ====================

@app.route('/api/peers', methods=['GET'])
def get_peers(headers="guest", body="anonymous"):
    """Get list of peers from central server."""
    try:
        peers_data = send_http_to_server('GET', '/get-list')
        if peers_data and peers_data.get('status') == 'success':
            return build_form_data(peers_data)
        else:
            return build_form_data({
                'status': 'error',
                'message': 'Could not retrieve peer list'
            })
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/send', methods=['POST'])
def send_direct(headers="guest", body="anonymous"):
    """Send direct P2P message to peer."""
    try:
        if body != "anonymous":
            params = parse_form_data(body)
            to_peer_id = params.get('to')
            message = params.get('message')
            
            if not to_peer_id or not message:
                return build_form_data({
                    'status': 'error',
                    'message': 'Missing to or message'
                })
            
            # Get peer info from server
            peer_info_data = send_http_to_server('POST', '/connect-peer', {
                'peer_id': to_peer_id
            })
            
            if peer_info_data and peer_info_data.get('status') == 'success':
                ip = peer_info_data.get('ip')
                port = int(peer_info_data.get('port'))
                p2p_port = port + 1000
                
                # Send P2P message
                msg_data = {
                    'from': peer_config['peer_id'],
                    'message': message,
                    'type': 'direct'
                }
                
                success = send_p2p_message(ip, p2p_port, msg_data)
                
                if success:
                    peer_config['messages'].append({
                        'from': 'You',
                        'to': to_peer_id,
                        'content': message,
                        'type': 'direct'
                    })
                    return build_form_data({
                        'status': 'success',
                        'message': 'Message sent'
                    })
                else:
                    return build_form_data({
                        'status': 'error',
                        'message': 'Failed to send message'
                    })
            else:
                return build_form_data({
                    'status': 'error',
                    'message': 'Peer not found'
                })
        
        return build_form_data({'status': 'error', 'message': 'No data'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/broadcast', methods=['POST'])
def broadcast(headers="guest", body="anonymous"):
    """Broadcast message to all peers."""
    try:
        if body != "anonymous":
            params = parse_form_data(body)
            message = params.get('message')
            
            if not message:
                return build_form_data({
                    'status': 'error',
                    'message': 'Missing message'
                })
            
            peers_data = send_http_to_server('GET', '/get-list')
            if peers_data and peers_data.get('status') == 'success':
                total = int(peers_data.get('total', 0))
                msg_data = {
                    'from': peer_config['peer_id'],
                    'message': message,
                    'type': 'broadcast'
                }
                
                sent_count = 0
                for i in range(total):
                    peer_data = peers_data.get('peer_{}'.format(i))
                    if peer_data:
                        parts = peer_data.split(',')
                        if len(parts) == 4:
                            pid, ip, port, username = parts
                            if pid != peer_config['peer_id']:
                                p2p_port = int(port) + 1000
                                if send_p2p_message(ip, p2p_port, msg_data):
                                    sent_count += 1
                
                peer_config['messages'].append({
                    'from': 'You [Broadcast]',
                    'content': message,
                    'type': 'broadcast'
                })
                
                return build_form_data({
                    'status': 'success',
                    'message': 'Broadcast to {} peers'.format(sent_count)
                })
        
        return build_form_data({'status': 'error', 'message': 'No data'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/channel/create', methods=['POST'])
def create_channel(headers="guest", body="anonymous"):
    """Create new channel."""
    try:
        if body != "anonymous":
            params = parse_form_data(body)
            channel_name = params.get('channel')
            
            if not channel_name:
                return build_form_data({
                    'status': 'error',
                    'message': 'Missing channel name'
                })
            
            result = send_http_to_server('POST', '/channel/create', {
                'channel': channel_name,
                'peer_id': peer_config['peer_id']
            })
            
            if result:
                return build_form_data(result)
        
        return build_form_data({'status': 'error', 'message': 'No data'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/channel/join', methods=['POST'])
def join_channel(headers="guest", body="anonymous"):
    """Join channel."""
    try:
        if body != "anonymous":
            params = parse_form_data(body)
            channel_name = params.get('channel')
            
            if not channel_name:
                return build_form_data({
                    'status': 'error',
                    'message': 'Missing channel name'
                })
            
            result = send_http_to_server('POST', '/channel/join', {
                'channel': channel_name,
                'peer_id': peer_config['peer_id']
            })
            
            if result:
                return build_form_data(result)
        
        return build_form_data({'status': 'error', 'message': 'No data'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/channel/send', methods=['POST'])
def send_to_channel(headers="guest", body="anonymous"):
    """Send message to channel."""
    try:
        if body != "anonymous":
            params = parse_form_data(body)
            channel_name = params.get('channel')
            message = params.get('message')
            
            if not channel_name or not message:
                return build_form_data({
                    'status': 'error',
                    'message': 'Missing channel or message'
                })
            
            # Get channel members
            members_data = send_http_to_server('POST', '/channel/members', {
                'channel': channel_name
            })
            
            if members_data and members_data.get('status') == 'success':
                total = int(members_data.get('total', 0))
                msg_data = {
                    'from': peer_config['peer_id'],
                    'message': message,
                    'type': 'channel',
                    'channel': channel_name
                }
                
                sent_count = 0
                for i in range(total):
                    member_data = members_data.get('member_{}'.format(i))
                    if member_data:
                        parts = member_data.split(',')
                        if len(parts) == 2:
                            pid, username = parts
                            if pid != peer_config['peer_id']:
                                # Get peer connection info
                                peer_info = send_http_to_server('POST', '/connect-peer', {
                                    'peer_id': pid
                                })
                                if peer_info and peer_info.get('status') == 'success':
                                    ip = peer_info.get('ip')
                                    port = int(peer_info.get('port'))
                                    p2p_port = port + 1000
                                    if send_p2p_message(ip, p2p_port, msg_data):
                                        sent_count += 1
                
                return build_form_data({
                    'status': 'success',
                    'message': 'Sent to {} members'.format(sent_count)
                })
            else:
                return build_form_data({
                    'status': 'error',
                    'message': 'Could not get channel members'
                })
        
        return build_form_data({'status': 'error', 'message': 'No data'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/p2p/message', methods=['POST'])
def receive_p2p_message(headers="guest", body="anonymous"):
    """Receive P2P message from another peer."""
    try:
        data = parse_form_data(body)
        peer_config['messages'].append({
            'from': data.get('from'),
            'content': data.get('message'),
            'type': data.get('type', 'direct'),
            'channel': data.get('channel', '')
        })
        print("[Peer] Message from {}: {}".format(
            data.get('from'), data.get('message')))
        return build_form_data({'status': 'success'})
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/channels', methods=['GET'])
def get_channels(headers="guest", body="anonymous"):
    """Get list of channels from central server via proxy."""
    try:
        result = send_http_to_server('GET', '/channels')
        if result:
            return build_form_data(result)
        else:
            return build_form_data({
                'status': 'error',
                'message': 'Could not retrieve channels'
            })
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

@app.route('/api/messages', methods=['GET'])
def get_messages(headers="guest", body="anonymous"):
    """Get received messages for polling."""
    try:
        result = {'status': 'success', 'count': len(peer_config['messages'])}
        
        idx = 0
        for msg in peer_config['messages']:
            msg_data = "{}|{}|{}|{}".format(
                msg.get('from', 'unknown'),
                msg.get('content', ''),
                msg.get('type', 'direct'),
                msg.get('channel', '')
            )
            result['msg_{}'.format(idx)] = msg_data
            idx += 1
        
        return build_form_data(result)
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='P2P Chat Peer')
    parser.add_argument('--username', required=True)
    parser.add_argument('--peer-port', type=int, required=True)
    parser.add_argument('--server-ip', default='127.0.0.1')
    parser.add_argument('--server-port', type=int, default=8000)
    
    args = parser.parse_args()
    
    peer_config['username'] = args.username
    peer_config['peer_port'] = args.peer_port
    peer_config['server_ip'] = args.server_ip
    peer_config['server_port'] = args.server_port
    
    # Start P2P listener thread
    p2p_thread = threading.Thread(target=start_p2p_listener)
    p2p_thread.daemon = True
    p2p_thread.start()
    
    # Register with central server
    peer_config['peer_id'] = 'peer_{}'.format(args.peer_port)
    reg_data = {
        'peer_id': peer_config['peer_id'],
        'username': args.username,
        'ip': '127.0.0.1',
        'port': args.peer_port
    }
    
    result = send_http_to_server('POST', '/submit-info', reg_data)
    if result and result.get('status') == 'success':
        print("[Peer] Registered as {}".format(peer_config['peer_id']))
    else:
        print("[Peer] Registration failed!")
    
    # Start WeApRous web server
    app.prepare_address('127.0.0.1', args.peer_port)
    print("=" * 60)
    print("[Peer] {} - Web UI: http://127.0.0.1:{}".format(
        args.username, args.peer_port))
    print("[Peer] P2P Port: {}".format(args.peer_port + 1000))
    print("=" * 60)
    app.run()