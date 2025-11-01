"""Message Router - Multiplexes single socket to multiple handlers.

This module solves the socket race condition where chat_client and operations_client
were both calling recv() on the same socket, causing messages to be randomly stolen
by whichever component called recv() first.

Architecture:
    Single socket → MessageRouter → Multiple queues → Multiple handlers

    - One receiver thread reads ALL messages from socket
    - Routes messages to appropriate queues based on prefix
    - Handlers get messages from their dedicated queues (no conflicts)
"""

import socket
import threading
import queue
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes messages from single socket to multiple handlers."""

    # Message prefixes for routing
    OPERATION_PREFIXES = ['OP_', 'OPERATION_', 'IIR_']
    # DM response messages (from server) - these go to chat queue for process_message()
    DM_RESPONSE_PREFIXES = ['DM_INBOX:', 'DM_CONVERSATION:', 'DM_MARKED_READ:']
    # OFFLINE goes to chat queue too (handled by process_message)
    SYSTEM_PREFIXES = ['WELCOME:', 'SERVER_SHUTDOWN:', 'ERROR:', 'SUCCESS:']

    def __init__(self, client_socket: socket.socket):
        """Initialize message router.

        Args:
            client_socket: The connected socket to route messages from
        """
        self.socket = client_socket
        self.running = True

        # Message queues for different subsystems
        self.chat_queue = queue.Queue()
        self.operations_queue = queue.Queue()
        # Note: DM responses go to chat_queue (processed by chat_client.process_message)

        # Connection status
        self.connected = True
        self.disconnect_callbacks = []

        # Start single receiver thread
        self.receiver_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True,
            name="MessageRouter-Receiver"
        )
        self.receiver_thread.start()
        logger.debug("MessageRouter started")

    def _receive_loop(self):
        """Single thread receives ALL messages and routes them.

        This eliminates the race condition where multiple threads were
        calling recv() on the same socket.
        """
        buffer = ""

        while self.running:
            try:
                # Receive data from socket
                data = self.socket.recv(4096).decode('utf-8')

                if not data:
                    # Connection closed
                    logger.debug("Socket closed by server")
                    break

                buffer += data

                # Process complete messages (ending with \n)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = line.strip()

                    if not message:
                        continue

                    # Route message to appropriate queue
                    self._route_message(message)

            except socket.timeout:
                # Timeout is OK, just check if we should keep running
                continue

            except Exception as e:
                if self.running:
                    logger.error(f"Error in message receiver: {e}")
                break

        # Connection lost or stopped
        self.connected = False
        self.running = False

        # Notify all disconnect callbacks
        for callback in self.disconnect_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")

        logger.debug("MessageRouter stopped")

    def _route_message(self, message: str):
        """Route message to appropriate queue based on prefix.

        Args:
            message: The message to route
        """
        # Check operations prefixes first (most specific)
        for prefix in self.OPERATION_PREFIXES:
            if message.startswith(prefix):
                self.operations_queue.put(message)
                logger.debug(f"Routed to operations: {message[:50]}")
                return

        # DM response messages from server go to chat queue
        # (They're processed by chat_client.process_message() to populate pending_responses)
        for prefix in self.DM_RESPONSE_PREFIXES:
            if message.startswith(prefix):
                self.chat_queue.put(message)
                logger.debug(f"Routed DM response to chat: {message[:50]}")
                return

        # Everything else goes to chat (includes CHAT:, HISTORY:, JOIN:, LEAVE:, OFFLINE:, etc.)
        self.chat_queue.put(message)
        logger.debug(f"Routed to chat: {message[:50]}")

    def get_chat_message(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get next chat message from queue.

        Args:
            timeout: How long to wait for message (None = wait forever, 0 = non-blocking)

        Returns:
            Message string or None if timeout/no message
        """
        try:
            if timeout == 0:
                # Non-blocking
                return self.chat_queue.get_nowait()
            else:
                return self.chat_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_operation_response(self, timeout: float = 5.0) -> str:
        """Get next operation response from queue.

        Args:
            timeout: How long to wait for response

        Returns:
            Response message

        Raises:
            TimeoutError: If no response received within timeout
        """
        try:
            return self.operations_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError(f"Operation response not received within {timeout}s")


    def send(self, message: str):
        """Send message to server.

        Args:
            message: Message to send (will append \n if not present)
        """
        if not message.endswith('\n'):
            message += '\n'

        try:
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def on_disconnect(self, callback: Callable[[], None]):
        """Register callback to be called when connection is lost.

        Args:
            callback: Function to call on disconnect
        """
        self.disconnect_callbacks.append(callback)

    def stop(self):
        """Stop the message router and close connection."""
        logger.debug("Stopping MessageRouter")
        self.running = False

        try:
            self.socket.close()
        except:
            pass

        # Wait for receiver thread to finish
        if self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=2.0)

    def is_connected(self) -> bool:
        """Check if connection is still active.

        Returns:
            True if connected, False otherwise
        """
        return self.connected and self.running
