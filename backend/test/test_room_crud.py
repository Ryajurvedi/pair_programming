import pytest
from unittest import mock
from sqlalchemy.orm import Session
from backend.app.crud import room_crud
from backend.app.models.room import Room 

# --- Mocking Fixtures and Objects ---

# Mock the Room Model used by the CRUD functions
class MockRoom:
    """A simple mock class simulating the Room model used in the CRUD functions."""
    def __init__(self, room_id: str, code_content: str):
        self.room_id = room_id
        self.code_content = code_content
        # Used for tracking changes in update_room_code
        self._initial_content = code_content

    # Helper method to simulate a commit change detection
    def was_content_updated(self):
        return self.code_content != self._initial_content
    
    # Required for mock testing as SQLAlchemy often returns a custom query object
    def __eq__(self, other):
        if isinstance(other, MockRoom):
            return self.room_id == other.room_id
        return NotImplemented

# Mock UUID generation globally for predictability in create_room
@pytest.fixture(autouse=True)
def mock_uuid(mocker):
    """Mocks uuid.uuid4() to return a predictable value for create_room testing."""
    mock_id = mocker.MagicMock()
    mock_id.hex = "0123456789abcdef" 
    
    # Mock the full uuid4 result (which is a UUID object)
    mock_uuid4_result = mocker.MagicMock()
    mock_uuid4_result.__str__.return_value = mock_id.hex 
    
    mocker.patch("backend.app.crud.room_crud.uuid.uuid4", return_value=mock_uuid4_result)


@pytest.fixture
def mock_db_session(mocker):
    """Provides a mocked SQLAlchemy Session."""
    mock_session = mocker.MagicMock(spec=Session)
    
    # Mock the query object chain
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    
    # Reset the default .first() return value for fresh tests
    mock_filter.first.return_value = None 
    
    return mock_session

# --- Tests for create_room ---

def test_create_room_success(mock_db_session, mocker):
    """Test successful room creation and DB interaction."""
    
    # The expected ID is the first 8 characters of the mocked uuid
    expected_room_id = "01234567"

    # We mock the Room model instantiation to ensure the correct values are passed
    mock_room_model = mocker.patch("backend.app.crud.room_crud.Room", side_effect=MockRoom)
    
    # 1. Execute the function
    returned_id = room_crud.create_room(mock_db_session)
    
    # 2. Assert the expected ID is returned
    assert returned_id == expected_room_id
    
    # 3. Assert the Room model was instantiated correctly
    mock_room_model.assert_called_once_with(
        room_id=expected_room_id, 
        code_content=""
    )
    
    # 4. Assert DB session commands were called
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


# --- Tests for get_room_code ---

def test_get_room_code_success(mock_db_session):
    """Test successful retrieval of code content."""
    test_id = "test_id_1"
    test_content = "def hello(): pass"
    
    # Setup the mock query to return a Room object
    mock_room = MockRoom(room_id=test_id, code_content=test_content)
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_room
    
    # 1. Execute the function
    code = room_crud.get_room_code(mock_db_session, test_id)
    
    # 2. Assert the correct code is returned
    assert code == test_content
    
    # 3. Assert the query was constructed correctly (checking the call to filter is sufficient)
    mock_db_session.query.assert_called_once_with(Room)
    mock_db_session.query.return_value.filter.assert_called_once()
    

def test_get_room_code_not_found(mock_db_session):
    """Test case where the room ID does not exist."""
    test_id = "non_existent"
    
    # Setup the mock query to return None (the default setup in the fixture)
    
    # 1. Execute the function
    code = room_crud.get_room_code(mock_db_session, test_id)
    
    # 2. Assert None is returned
    assert code is None


# --- Tests for get_room_by_id ---

def test_get_room_by_id_success(mock_db_session):
    """Test successful retrieval of the Room object."""
    test_id = "test_id_2"
    
    # Setup the mock query to return a Room object
    expected_room = MockRoom(room_id=test_id, code_content="")
    mock_db_session.query.return_value.filter.return_value.first.return_value = expected_room
    
    # 1. Execute the function
    room = room_crud.get_room_by_id(mock_db_session, test_id)
    
    # 2. Assert the correct object is returned
    assert room == expected_room
    assert room.room_id == test_id
    
    
def test_get_room_by_id_not_found(mock_db_session):
    """Test case where the Room object is not found."""
    test_id = "non_existent_2"
    
    # Setup the mock query to return None (the default setup in the fixture)
    
    # 1. Execute the function
    room = room_crud.get_room_by_id(mock_db_session, test_id)
    
    # 2. Assert None is returned
    assert room is None


# --- Tests for update_room_code ---

def test_update_room_code_success(mock_db_session):
    """Test successful update of code content and commit."""
    test_id = "test_id_3"
    new_content = "print('new code')"
    initial_room = MockRoom(room_id=test_id, code_content="old code")
    
    # Setup the mock query to return the Room object
    mock_db_session.query.return_value.filter.return_value.first.return_value = initial_room
    
    # 1. Execute the function
    room_crud.update_room_code(mock_db_session, test_id, new_content)
    
    # 2. Assert the object's attribute was updated
    assert initial_room.code_content == new_content
    
    # 3. Assert DB session commands were called
    mock_db_session.commit.assert_called_once()


def test_update_room_code_room_not_found(mock_db_session):
    """Test update when the room does not exist (should do nothing)."""
    test_id = "non_existent_3"
    new_content = "bad update"
    
    # Setup the mock query to return None (the default setup)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    # 1. Execute the function
    room_crud.update_room_code(mock_db_session, test_id, new_content)
    
    # 2. Assert DB session commands were NOT called
    mock_db_session.commit.assert_not_called()