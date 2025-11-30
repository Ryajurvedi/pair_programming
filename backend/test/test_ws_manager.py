import pytest
from unittest import mock
from unittest.mock import AsyncMock
from backend.app.core.ws_manager import ConnectionManager

# --- Fixtures ---

@pytest.fixture
def manager():
    """Provides a fresh ConnectionManager instance for each test."""
    return ConnectionManager()

@pytest.fixture
def mock_websocket_factory():
    """
    Returns a factory function to create a mocked WebSocket object.
    Each mock has an AsyncMock for accept and send_text.
    """
    def _factory(name: str):
        mock_ws = mock.MagicMock(spec=['accept', 'send_text', 'close'], name=name)
        # Ensure accept and send_text are awaitable
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        return mock_ws
    return _factory

# --- Tests ---

@pytest.mark.asyncio
async def test_connect_new_room(manager, mock_websocket_factory):
    """Test connecting a WebSocket to a room that doesn't exist yet."""
    room_id = "room_a"
    ws = mock_websocket_factory("ws1")
    
    # 1. Connect
    await manager.connect(ws, room_id)
    
    # 2. Assert connection logic
    ws.accept.assert_awaited_once()
    assert room_id in manager.active_connections
    assert manager.active_connections[room_id] == [ws]

@pytest.mark.asyncio
async def test_connect_existing_room(manager, mock_websocket_factory):
    """Test connecting a second WebSocket to an existing room."""
    room_id = "room_b"
    ws1 = mock_websocket_factory("ws1")
    ws2 = mock_websocket_factory("ws2")

    # Setup existing connection
    manager.active_connections[room_id] = [ws1]
    
    # 1. Connect the second socket
    await manager.connect(ws2, room_id)
    
    # 2. Assert connection logic
    ws2.accept.assert_awaited_once()
    assert room_id in manager.active_connections
    assert manager.active_connections[room_id] == [ws1, ws2]

def test_disconnect_last_user(manager, mock_websocket_factory):
    """Test disconnecting the last user, which should remove the room key."""
    room_id = "room_c"
    ws = mock_websocket_factory("ws1")
    
    # Setup state
    manager.active_connections[room_id] = [ws]
    
    # 1. Disconnect
    manager.disconnect(ws, room_id)
    
    # 2. Assert disconnection logic
    assert room_id not in manager.active_connections
    assert not manager.active_connections # Ensure the dictionary is empty

def test_disconnect_middle_user(manager, mock_websocket_factory):
    """Test disconnecting one user from a room with multiple users."""
    room_id = "room_d"
    ws1 = mock_websocket_factory("ws1")
    ws2 = mock_websocket_factory("ws2")
    ws3 = mock_websocket_factory("ws3")
    
    # Setup state
    manager.active_connections[room_id] = [ws1, ws2, ws3]
    
    # 1. Disconnect the middle user (ws2)
    manager.disconnect(ws2, room_id)
    
    # 2. Assert disconnection logic
    assert room_id in manager.active_connections
    assert ws2 not in manager.active_connections[room_id]
    assert len(manager.active_connections[room_id]) == 2
    assert manager.active_connections[room_id] == [ws1, ws3]

def test_disconnect_non_existent_room(manager, mock_websocket_factory):
    """Test calling disconnect on a room that doesn't exist (should not fail)."""
    room_id = "non_existent"
    ws = mock_websocket_factory("ws1")
    
    # No exception should be raised
    manager.disconnect(ws, room_id)
    assert not manager.active_connections # Should still be empty

@pytest.mark.asyncio
async def test_broadcast_to_multiple_receivers(manager, mock_websocket_factory):
    """Test broadcast sends a message to all users in the room except the sender."""
    room_id = "room_e"
    sender = mock_websocket_factory("sender")
    receiver1 = mock_websocket_factory("receiver1")
    receiver2 = mock_websocket_factory("receiver2")
    message = "test message"
    
    # Setup state
    manager.active_connections[room_id] = [sender, receiver1, receiver2]
    
    # 1. Broadcast
    await manager.broadcast(message, room_id, sender)
    
    # 2. Assertions
    # Sender should NOT receive the message
    sender.send_text.assert_not_awaited()
    
    # Receivers SHOULD receive the message
    receiver1.send_text.assert_awaited_once_with(message)
    receiver2.send_text.assert_awaited_once_with(message)

@pytest.mark.asyncio
async def test_broadcast_no_other_receivers(manager, mock_websocket_factory):
    """Test broadcast when the sender is the only one in the room."""
    room_id = "room_f"
    sender = mock_websocket_factory("sender")
    message = "test message"
    
    # Setup state
    manager.active_connections[room_id] = [sender]
    
    # 1. Broadcast
    await manager.broadcast(message, room_id, sender)
    
    # 2. Assertions
    # Sender should NOT receive the message, and no other calls should be made
    sender.send_text.assert_not_awaited()

@pytest.mark.asyncio
async def test_broadcast_non_existent_room(manager, mock_websocket_factory):
    """Test calling broadcast on a room that doesn't exist (should not fail)."""
    room_id = "non_existent_room_g"
    sender = mock_websocket_factory("sender")
    
    # No exception should be raised
    await manager.broadcast("message", room_id, sender)
    # The sender's mock should definitely not be called, as it's not connected anywhere
    sender.send_text.assert_not_awaited()