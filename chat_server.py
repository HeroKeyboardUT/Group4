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

# Global tracking list of active peers
# Structure: {"peer_id": {"ip": "x.x.x.x", "port": xxxx, "username": "xxx"}}
active_peers = {}

# Channel management
# Structure: {"channel_name": {"peers": [], "messages": [], "owner": "peer_id"}}
channels = {"general": {"peers": [], "messages": [], "owner": "system"}}

app = WeApRous()

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

@app.route('/login', methods=['POST'])
def login(headers="", body=""):
    """
    User login endpoint.
    
    Expected body: username=user1&password=pass123
    Returns: status=success&peer_id=unique_id&message=Login+successful
    """
    try:
        data = parse_form_data(body)
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username and password:
            peer_id = "peer_{}".format(len(active_peers) + 1)
            print("[ChatServer] User '{}' logged in as {}".format(username, peer_id))
            
            return build_form_data({
                'status': 'success',
                'peer_id': peer_id,
                'message': 'Login successful'
            })
        else:
            return build_form_data({
                'status': 'error',
                'message': 'Invalid credentials'
            })
    except Exception as e:
        print("[ChatServer] Login error: {}".format(e))
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/submit-info', methods=['POST'])
def submit_info(headers="", body=""):
    """
    Peer registration endpoint.
    
    Expected body: peer_id=peer_1&ip=127.0.0.1&port=5001&username=Alice
    Returns: status=success&message=Peer+registered&total_peers=5
    """
    try:
        data = parse_form_data(body)
        peer_id = data.get('peer_id')
        ip = data.get('ip')
        port = data.get('port')
        username = data.get('username', 'Anonymous')
        
        if peer_id and ip and port:
            active_peers[peer_id] = {
                'ip': ip,
                'port': int(port),
                'username': username
            }
            
            print("[ChatServer] Registered peer: {} at {}:{}".format(
                username, ip, port))
            
            return build_form_data({
                'status': 'success',
                'message': 'Peer registered successfully',
                'total_peers': len(active_peers)
            })
        else:
            return build_form_data({
                'status': 'error',
                'message': 'Missing required fields'
            })
    except Exception as e:
        print("[ChatServer] Submit-info error: {}".format(e))
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/get-list', methods=['GET'])
def get_list(headers="", body=""):
    """
    Get list of active peers.
    
    Returns: status=success&total=3&peer_0=peer_1,127.0.0.1,5001,Alice&peer_1=...
    """
    try:
        result = {'status': 'success', 'total': len(active_peers)}
        
        idx = 0
        for peer_id, info in active_peers.items():
            peer_data = "{},{},{},{}".format(
                peer_id,
                info['ip'],
                info['port'],
                info['username']
            )
            result['peer_{}'.format(idx)] = peer_data
            idx += 1
        
        print("[ChatServer] Sent peer list: {} peers".format(len(active_peers)))
        return build_form_data(result)
        
    except Exception as e:
        print("[ChatServer] Get-list error: {}".format(e))
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/add-list', methods=['POST'])
def add_list(headers="", body=""):
    """
    Add peer to specific channel.
    
    Expected body: peer_id=peer_1&channel=general
    Returns: status=success&message=Added+to+channel&channel=general
    """
    try:
        data = parse_form_data(body)
        peer_id = data.get('peer_id')
        channel_name = data.get('channel', 'general')
        
        if channel_name not in channels:
            channels[channel_name] = {
                'peers': [],
                'messages': [],
                'owner': peer_id
            }
        
        if peer_id not in channels[channel_name]['peers']:
            channels[channel_name]['peers'].append(peer_id)
            
            print("[ChatServer] Added {} to channel '{}'".format(
                peer_id, channel_name))
            
            return build_form_data({
                'status': 'success',
                'message': 'Added to channel',
                'channel': channel_name
            })
        else:
            return build_form_data({
                'status': 'info',
                'message': 'Already in channel'
            })
    except Exception as e:
        print("[ChatServer] Add-list error: {}".format(e))
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/channels', methods=['GET'])
def list_channels(headers="", body=""):
    """
    List all available channels.
    
    Returns: status=success&total=2&channel_0=general,system,5&channel_1=random,peer_1,3
    Format: channel_name,creator,member_count
    """
    try:
        result = {'status': 'success', 'total': len(channels)}
        
        idx = 0
        for name, data in channels.items():
            channel_data = "{},{},{}".format(
                name, 
                data['owner'], 
                len(data['peers'])
            )
            result['channel_{}'.format(idx)] = channel_data
            idx += 1
        
        print("[ChatServer] Sent channel list: {} channels".format(len(channels)))
        return build_form_data(result)
    except Exception as e:
        print("[ChatServer] Channels error: {}".format(e))
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/connect-peer', methods=['POST'])
def connect_peer(headers="", body=""):
    """
    Get specific peer connection info.
    
    Expected body: peer_id=peer_1
    Returns: status=success&ip=127.0.0.1&port=5001&username=Alice
    """
    try:
        data = parse_form_data(body)
        peer_id = data.get('peer_id')
        
        if peer_id in active_peers:
            peer_info = active_peers[peer_id]
            return build_form_data({
                'status': 'success',
                'ip': peer_info['ip'],
                'port': peer_info['port'],
                'username': peer_info['username']
            })
        else:
            return build_form_data({
                'status': 'error',
                'message': 'Peer not found'
            })
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/channel/create', methods=['POST'])
def create_channel(headers="", body=""):
    """
    Create new channel.
    
    Expected body: channel=mychannel&peer_id=peer_1
    Returns: status=success&channel=mychannel
    """
    try:
        data = parse_form_data(body)
        channel_name = data.get('channel')
        peer_id = data.get('peer_id', 'anonymous')
        
        if not channel_name:
            return build_form_data({
                'status': 'error',
                'message': 'Channel name required'
            })
        
        if channel_name in channels:
            return build_form_data({
                'status': 'error',
                'message': 'Channel already exists'
            })
        
        channels[channel_name] = {
            'peers': [peer_id] if peer_id != 'anonymous' else [],
            'messages': [],
            'owner': peer_id
        }
        
        print("[ChatServer] Channel '{}' created by {}".format(
            channel_name, peer_id))
        
        return build_form_data({
            'status': 'success',
            'channel': channel_name,
            'message': 'Channel created'
        })
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/channel/join', methods=['POST'])
def join_channel(headers="", body=""):
    """
    Join existing channel.
    
    Expected body: channel=general&peer_id=peer_1
    Returns: status=success&channel=general
    """
    try:
        data = parse_form_data(body)
        channel_name = data.get('channel')
        peer_id = data.get('peer_id')
        
        if not channel_name or not peer_id:
            return build_form_data({
                'status': 'error',
                'message': 'Missing channel or peer_id'
            })
        
        if channel_name not in channels:
            return build_form_data({
                'status': 'error',
                'message': 'Channel not found'
            })
        
        if peer_id not in channels[channel_name]['peers']:
            channels[channel_name]['peers'].append(peer_id)
        
        print("[ChatServer] {} joined channel '{}'".format(
            peer_id, channel_name))
        
        return build_form_data({
            'status': 'success',
            'channel': channel_name,
            'message': 'Joined channel'
        })
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})


@app.route('/channel/members', methods=['POST'])
def channel_members(headers="", body=""):
    """
    Get channel members.
    
    Expected body: channel=general
    Returns: status=success&total=3&member_0=peer_1,Alice&member_1=...
    """
    try:
        data = parse_form_data(body)
        channel_name = data.get('channel')
        
        if channel_name not in channels:
            return build_form_data({
                'status': 'error',
                'message': 'Channel not found'
            })
        
        channel = channels[channel_name]
        result = {'status': 'success', 'total': len(channel['peers'])}
        
        idx = 0
        for peer_id in channel['peers']:
            if peer_id in active_peers:
                username = active_peers[peer_id]['username']
                result['member_{}'.format(idx)] = "{},{}".format(
                    peer_id, username)
                idx += 1
        
        return build_form_data(result)
    except Exception as e:
        return build_form_data({'status': 'error', 'message': str(e)})


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