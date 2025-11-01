"""Configuration reader for chat server/client.

Implements hybrid configuration approach:
1. Check config file (chat_config.json)
2. Check Tailscale hostname resolution
3. Fallback to hardcoded defaults
"""

import json
import os
import socket
from typing import Tuple, Optional


class ChatConfig:
    """Configuration manager for chat server and client."""

    # Default fallback values
    DEFAULT_SERVER_HOST = "0.0.0.0"
    DEFAULT_SERVER_PORT = 7331
    DEFAULT_CLIENT_SERVER = "100.115.233.16"  # main-win Tailscale IP
    DEFAULT_CLIENT_PORT = 7331

    def __init__(self, config_path: str = "chat_config.json"):
        """Initialize config reader.

        Args:
            config_path: Path to config file (default: chat_config.json)
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file.

        Returns:
            Config dict or empty dict if file doesn't exist
        """
        # Try to load from current directory
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load {self.config_path}: {e}")
                return {}

        # Try to load from script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, self.config_path)
        if os.path.exists(alt_path):
            try:
                with open(alt_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load {alt_path}: {e}")
                return {}

        # No config file found - use defaults
        return {}

    def get_server_config(self) -> Tuple[str, int]:
        """Get server binding configuration.

        Returns:
            Tuple of (host, port) for server to bind to
        """
        server_cfg = self.config.get('server', {})

        host = server_cfg.get('host', self.DEFAULT_SERVER_HOST)
        port = server_cfg.get('port', self.DEFAULT_SERVER_PORT)

        return host, port

    def get_client_config(self) -> Tuple[str, int]:
        """Get client server address configuration.

        Implements priority order:
        1. Config file value
        2. Tailscale hostname resolution
        3. Hardcoded fallback

        Returns:
            Tuple of (server_address, port) for client to connect to
        """
        client_cfg = self.config.get('client', {})
        tailscale_cfg = self.config.get('tailscale', {})

        server_address = client_cfg.get('server_address', 'auto')
        port = client_cfg.get('server_port', self.DEFAULT_CLIENT_PORT)

        # Handle 'auto' - try Tailscale hostname resolution
        if server_address == 'auto':
            if tailscale_cfg.get('enabled', True):
                hostname = tailscale_cfg.get('hostname', 'chat-server')
                resolved = self._resolve_tailscale_hostname(hostname)
                if resolved:
                    return resolved, port

            # Auto failed, fall back to default
            server_address = self.DEFAULT_CLIENT_SERVER

        return server_address, port

    def _resolve_tailscale_hostname(self, hostname: str) -> Optional[str]:
        """Try to resolve Tailscale hostname to IP address.

        Tries multiple formats:
        1. hostname (e.g., "chat-server")
        2. hostname.tail-scale.ts.net
        3. Various Tailscale domain formats

        Args:
            hostname: Tailscale hostname to resolve

        Returns:
            Resolved IP address or None if resolution failed
        """
        # Try different Tailscale hostname formats
        formats_to_try = [
            hostname,  # Simple hostname
            f"{hostname}.tail-scale.ts.net",  # Full Tailscale domain
            f"{hostname}.local",  # mDNS fallback
        ]

        for name in formats_to_try:
            try:
                # Try to resolve hostname
                ip = socket.gethostbyname(name)
                # Verify it's a valid IP (not localhost)
                if ip and ip != '127.0.0.1':
                    print(f"[INFO] Resolved '{hostname}' to {ip}")
                    return ip
            except socket.gaierror:
                # Resolution failed, try next format
                continue
            except Exception as e:
                print(f"[DEBUG] Error resolving {name}: {e}")
                continue

        # All resolution attempts failed
        print(f"[WARNING] Could not resolve Tailscale hostname '{hostname}'")
        return None

    def get_server_display_address(self) -> str:
        """Get the address server is actually listening on.

        Returns:
            Display string for server address
        """
        host, port = self.get_server_config()

        # If listening on all interfaces, show local IPs
        if host == "0.0.0.0":
            try:
                # Try to get Tailscale IP
                tailscale_ip = self._get_tailscale_ip()
                if tailscale_ip:
                    return f"{tailscale_ip}:{port} (and all interfaces)"
                else:
                    hostname = socket.gethostname()
                    return f"{hostname}:{port} (all interfaces)"
            except:
                return f"0.0.0.0:{port} (all interfaces)"
        else:
            return f"{host}:{port}"

    def _get_tailscale_ip(self) -> Optional[str]:
        """Try to get local Tailscale IP address.

        Returns:
            Tailscale IP or None
        """
        try:
            # Get all network interfaces
            import subprocess
            result = subprocess.run(['ip', 'addr', 'show', 'tailscale0'],
                                    capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                # Parse IP from output
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
        except:
            pass

        return None


# Singleton instance
_config_instance = None


def get_config() -> ChatConfig:
    """Get singleton config instance.

    Returns:
        ChatConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ChatConfig()
    return _config_instance
