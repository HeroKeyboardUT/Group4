#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# Hybrid Chat Application - Central Server (Tracker)
#

"""
apps.chat_server
~~~~~~~~~~~~~~~~~

Central server for peer discovery and tracking in hybrid chat system.
Implements RESTful APIs for peer registration and discovery.
Uses form data format for all communication.
"""

from daemon.weaprous import WeApRous
import json

# Global tracking list of active peers
# Structure: {"peer_id": {"ip": "x.x.x.x", "port": xxxx, "username": "xxx"}}
active_peers = {}

# Channel management
# Structure: {"channel_name": {"peers": [], "messages": [], "owner": "peer_id"}}
channels = {"general": {"peers": [], "owner": "system"}}

app = WeApRous()

@app.route('/submit-info', methods=['POST'])
def submit_info(headers="", body=""):
    """Peer registration."""
    try:
        data = json.loads(body)
        peer_id = data.get('peer_id')
        
        active_peers[peer_id] = {
            'ip': data.get('ip'),
            'port': int(data.get('port')),
            'username': data.get('username', 'Anonymous')
        }
        
        print("[Server] Registered: {}".format(peer_id))
        return json.dumps({'status': 'success', 'total': len(active_peers)})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@app.route('/get-list', methods=['GET'])
def get_list(headers="", body=""):
    """Get peer list."""
    peers = []
    for peer_id, info in active_peers.items():
        peers.append({
            'id': peer_id,
            'ip': info['ip'],
            'port': info['port'],
            'username': info['username']
        })
    
    return json.dumps({'status': 'success', 'peers': peers})

@app.route('/channels', methods=['GET'])
def list_channels(headers="", body=""):
    """List channels."""
    channel_list = []
    for name, data in channels.items():
        channel_list.append({
            'name': name,
            'owner': data['owner'],
            'members': len(data['peers'])
        })
    
    return json.dumps({'status': 'success', 'channels': channel_list})

@app.route('/connect-peer', methods=['POST'])
def connect_peer(headers="", body=""):
    """Get peer connection info."""
    try:
        data = json.loads(body)
        peer_id = data.get('peer_id')
        
        if peer_id in active_peers:
            info = active_peers[peer_id]
            return json.dumps({
                'status': 'success',
                'ip': info['ip'],
                'port': info['port'],
                'username': info['username']
            })
        
        return json.dumps({'status': 'error', 'message': 'Peer not found'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@app.route('/channel/create', methods=['POST'])
def create_channel(headers="", body=""):
    """Create channel."""
    try:
        data = json.loads(body)
        channel = data.get('channel')
        peer_id = data.get('peer_id')
        
        if channel in channels:
            return json.dumps({'status': 'error', 'message': 'Channel exists'})
        
        channels[channel] = {'peers': [peer_id], 'owner': peer_id}
        return json.dumps({'status': 'success'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@app.route('/channel/join', methods=['POST'])
def join_channel(headers="", body=""):
    """Join channel."""
    try:
        data = json.loads(body)
        channel = data.get('channel')
        peer_id = data.get('peer_id')
        
        if channel not in channels:
            return json.dumps({'status': 'error', 'message': 'Channel not found'})
        
        if peer_id not in channels[channel]['peers']:
            channels[channel]['peers'].append(peer_id)
        
        return json.dumps({'status': 'success'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

@app.route('/channel/members', methods=['POST'])
def channel_members(headers="", body=""):
    """Get channel members."""
    try:
        data = json.loads(body)
        channel = data.get('channel')
        
        if channel not in channels:
            return json.dumps({'status': 'error'})
        
        members = []
        for peer_id in channels[channel]['peers']:
            if peer_id in active_peers:
                members.append({
                    'id': peer_id,
                    'username': active_peers[peer_id]['username']
                })
        
        return json.dumps({'status': 'success', 'members': members})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

# ==================== API Aliases (Match assignment requirements) ====================

@app.route('/add-list', methods=['POST'])
def add_list(headers="", body=""):
    """Alias for /submit-info to match assignment requirement (add peer to list)."""
    return submit_info(headers, body)

@app.route('/login', methods=['POST'])
def login(headers="", body=""):
    """Login endpoint to match assignment requirement.
    Chat server doesn't require authentication, always returns success.
    """
    return json.dumps({'status': 'success', 'message': 'Chat server does not require authentication'})

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='ChatServer',
        description='Central server for hybrid chat system'
    )
    parser.add_argument('--server-ip', default='127.0.0.1')
    parser.add_argument('--server-port', type=int, default=8000)
    
    args = parser.parse_args()
    
    app.prepare_address(args.server_ip, args.server_port)
    
    print("=" * 50)
    print("Chat Central Server (Tracker)")
    print("Link: http://{}:{}".format(args.server_ip, args.server_port))
    print("=" * 50)
    print("\nAvailable APIs:")
    print("  POST /login")
    print("  POST /submit-info")
    print("  GET  /get-list")
    print("  POST /add-list")
    print("  GET  /channels")
    print("  POST /connect-peer")
    print("  POST /channel/create")
    print("  POST /channel/join")
    print("  POST /channel/members")
    print("=" * 50)
    
    app.run()