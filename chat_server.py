#!/usr/bin/env python3
"""
Secret Chat Server - 90s Hacker Style
Runs on main-win (100.115.233.16)
"""

import socket
import threading
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, Set
from operations_db import OperationsDB


class ChatServer:
    """Simple chat server for Tailscale network."""

    def __init__(self, host='100.115.233.16', port=7331):  # 1337 reversed ;)
        self.host = host
        self.port = port
        self.clients: Dict[socket.socket, str] = {}  # socket -> username
        self.usernames: Set[str] = set()
        self.running = False
        self.server_socket = None

        # Initialize database for offline messages
        self.init_database()

        # Initialize operations database
        self.ops_db = OperationsDB('operations.db')

    def init_database(self):
        """Initialize SQLite database for offline messages."""
        self.db = sqlite3.connect('chat_messages.db', check_same_thread=False)
        self.db_lock = threading.Lock()

        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                delivered INTEGER DEFAULT 0
            )
        ''')
        self.db.commit()

    def store_offline_message(self, recipient, sender, message):
        """Store message for offline user."""
        with self.db_lock:
            cursor = self.db.cursor()
            cursor.execute(
                'INSERT INTO offline_messages (recipient, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                (recipient, sender, message, datetime.now().isoformat())
            )
            self.db.commit()

    def get_offline_messages(self, username):
        """Retrieve offline messages for user."""
        with self.db_lock:
            cursor = self.db.cursor()
            cursor.execute(
                'SELECT sender, message, timestamp FROM offline_messages WHERE recipient = ? AND delivered = 0',
                (username,)
            )
            messages = cursor.fetchall()

            # Mark as delivered
            cursor.execute(
                'UPDATE offline_messages SET delivered = 1 WHERE recipient = ?',
                (username,)
            )
            self.db.commit()

            return messages

    def broadcast(self, message, sender_socket=None):
        """Send message to all connected clients."""
        disconnected = []

        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.send((message + '\n').encode('utf-8'))
                except:
                    disconnected.append(client_socket)

        # Clean up disconnected clients
        for client_socket in disconnected:
            self.remove_client(client_socket)

    def send_to_user(self, username, message):
        """Send message to specific user."""
        for client_socket, client_username in self.clients.items():
            if client_username == username:
                try:
                    client_socket.send((message + '\n').encode('utf-8'))
                    return True
                except:
                    self.remove_client(client_socket)
                    return False
        return False

    def handle_client(self, client_socket, address):
        """Handle individual client connection."""
        username = None

        try:
            # Get username
            client_socket.send(b'USERNAME:\n')
            username = client_socket.recv(1024).decode('utf-8').strip()

            # Check if username is taken
            while username in self.usernames:
                client_socket.send(b'USERNAME_TAKEN:\n')
                username = client_socket.recv(1024).decode('utf-8').strip()

            # Add client
            self.clients[client_socket] = username
            self.usernames.add(username)

            print(f"[+] {username} connected from {address}")

            # Send welcome message
            client_socket.send(f'WELCOME:{username}\n'.encode('utf-8'))

            # Send user list
            user_list = ','.join(self.usernames)
            self.broadcast(f'USERLIST:{user_list}')

            # Send offline messages
            offline_msgs = self.get_offline_messages(username)
            if offline_msgs:
                for sender, msg, timestamp in offline_msgs:
                    client_socket.send(f'OFFLINE:{sender}:{timestamp}:{msg}\n'.encode('utf-8'))

            # Announce join
            self.broadcast(f'JOIN:{username}', client_socket)

            # Handle messages
            buffer = ""
            while self.running:
                try:
                    chunk = client_socket.recv(65536).decode('utf-8')
                    if not chunk:
                        break

                    buffer += chunk
                    print(f"DEBUG: Received chunk of {len(chunk)} bytes, buffer now {len(buffer)} bytes")

                    # Process complete messages (ending with \n)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        data = line.strip()

                        if not data:
                            continue

                        # Parse message
                        if data.startswith('MSG:'):
                            # Group message
                            message = data[4:]
                            print(f"[{username}] {message}")
                            self.broadcast(f'MSG:{username}:{message}', client_socket)

                        elif data.startswith('DM:'):
                            # Direct message format: DM:recipient:message
                            parts = data[3:].split(':', 1)
                            if len(parts) == 2:
                                recipient, message = parts

                                # Try to send, if offline store it
                                if not self.send_to_user(recipient, f'DM:{username}:{message}'):
                                    self.store_offline_message(recipient, username, message)
                                    client_socket.send(f'INFO:Message to {recipient} stored (offline)\n'.encode('utf-8'))

                        # OPERATIONS COMMANDS
                        elif data.startswith('OP_LIST:'):
                            # Get list of all operations
                            ops = self.ops_db.get_all_operations()
                            response = json.dumps(ops)
                            client_socket.send(f'OP_LIST:{response}\n'.encode('utf-8'))

                        elif data.startswith('OP_CREATE:'):
                            # Create new operation: OP_CREATE:name:password:description
                            parts = data[10:].split(':', 2)
                            if len(parts) >= 2:
                                op_name = parts[0]
                                op_password = parts[1]
                                op_description = parts[2] if len(parts) > 2 else ""
                                success, msg = self.ops_db.create_operation(op_name, username, op_password, op_description)
                                client_socket.send(f'OP_CREATE_RESULT:{success}:{msg}\n'.encode('utf-8'))

                        elif data.startswith('OP_VERIFY:'):
                            # Verify operation password: OP_VERIFY:name:password
                            parts = data[10:].split(':', 1)
                            if len(parts) == 2:
                                op_name, op_password = parts
                                valid = self.ops_db.verify_operation_password(op_name, op_password)
                                client_socket.send(f'OP_VERIFY_RESULT:{valid}\n'.encode('utf-8'))

                        elif data.startswith('OP_POSTS:'):
                            # Get posts for operation: OP_POSTS:name
                            op_name = data[9:]
                            posts = self.ops_db.get_operation_posts(op_name)
                            response = json.dumps(posts)
                            client_socket.send(f'OP_POSTS:{response}\n'.encode('utf-8'))

                        elif data.startswith('OP_POST:'):
                            # Add post: OP_POST:op_name:comment:filename:file_data_base64
                            parts = data[8:].split(':', 3)  # Split into 4 parts: op_name, comment, filename, file_data
                            if len(parts) >= 2:
                                op_name = parts[0]
                                comment = parts[1]
                                filename = parts[2] if len(parts) > 2 and parts[2] else None
                                file_data_b64 = parts[3] if len(parts) > 3 and parts[3] else None

                                print(f"OP_POST: op={op_name}, comment={comment[:50]}, filename={filename}, has_file={bool(file_data_b64)}, file_size={len(file_data_b64) if file_data_b64 else 0}")

                                # Save file to disk if provided
                                file_path = None
                                if filename and file_data_b64:
                                    import base64
                                    import os
                                    # Create uploads directory if it doesn't exist
                                    os.makedirs('uploads', exist_ok=True)
                                    # Generate unique filename
                                    import time
                                    file_path = f'uploads/{int(time.time())}_{filename}'
                                    try:
                                        file_data = base64.b64decode(file_data_b64)
                                        with open(file_path, 'wb') as f:
                                            f.write(file_data)
                                        print(f"File saved: {file_path} ({len(file_data)} bytes)")
                                    except Exception as e:
                                        print(f"Error saving file: {e}")
                                        file_path = None

                                success, msg = self.ops_db.add_post(op_name, username, comment, filename, file_path)
                                print(f"add_post result: success={success}, msg={msg}")
                                client_socket.send(f'OP_POST_RESULT:{success}:{msg}\n'.encode('utf-8'))

                        elif data.startswith('OP_INFO:'):
                            # Get operation info: OP_INFO:name
                            op_name = data[8:]
                            op_info = self.ops_db.get_operation_info(op_name)
                            response = json.dumps(op_info) if op_info else "null"
                            client_socket.send(f'OP_INFO:{response}\n'.encode('utf-8'))

                        elif data.startswith('OP_FILE:'):
                            # Download file: OP_FILE:post_id
                            post_id = data[8:]
                            file_data_b64 = self.ops_db.get_file_data(int(post_id))
                            response = file_data_b64 if file_data_b64 else "null"
                            client_socket.send(f'OP_FILE:{response}\n'.encode('utf-8'))

                except Exception as e:
                    print(f"Error handling message from {username}: {e}")
                    break

        except Exception as e:
            print(f"Error with client {address}: {e}")

        finally:
            self.remove_client(client_socket)
            if username:
                print(f"[-] {username} disconnected")
                self.broadcast(f'LEAVE:{username}')

    def remove_client(self, client_socket):
        """Remove client from active connections."""
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            self.usernames.discard(username)
            try:
                client_socket.close()
            except:
                pass

    def start(self):
        """Start the chat server."""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"[*] Chat server started on {self.host}:{self.port}")
            print(f"[*] Waiting for connections...")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")

        except Exception as e:
            print(f"Server error: {e}")

        finally:
            self.stop()

    def stop(self):
        """Stop the chat server."""
        self.running = False

        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Close database
        if hasattr(self, 'db'):
            self.db.close()

        print("[*] Server stopped")


def main():
    """Run the chat server."""
    print("=" * 50)
    print("  ░▒▓█ SECRET CHAT SERVER █▓▒░")
    print("  90s Hacker Edition")
    print("=" * 50)

    server = ChatServer()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.stop()


if __name__ == "__main__":
    main()
