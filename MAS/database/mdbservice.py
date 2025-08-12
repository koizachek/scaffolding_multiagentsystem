import os, bcrypt, logging
from typing import Any, Literal
from dotenv import load_dotenv
from pymongo import DESCENDING
from pymongo.mongo_client import MongoClient
from datetime import datetime

from MAS.database.dtos import *

load_dotenv()
def _construct_uri_from_env() -> str:
    return f"mongodb+srv://{os.environ['MONGODB_MAS_NAME']}:{os.environ['MONGODB_MAS_KEY']}@mas.oxzqvr2.mongodb.net/?retryWrites=true&w=majority&appName=MAS"

logger = logging.getLogger(__name__)

class MDBServiceException(Exception): pass
class IndexOverrideException(MDBServiceException): pass
class DatabaseConnectionException(MDBServiceException): pass
class ProfileAlreadyExistsException(MDBServiceException): pass
class ProfileNotFoundException(MDBServiceException): pass
class MissingIndexException(MDBServiceException): pass
class FalsePasswordException(MDBServiceException): pass

class MDBService:
    """Service for interacting with MongoDB Scaffolding database for storing and retrieving session data and profiles."""
    
    def __init__(self, uri: Optional[str] = None) -> None:
        """
        Initializes MongoDB client, loads the sessions collection and it's indexes for validation.

        Raises:
            DatabaseConnectionException: If connection to MongoDB fails.
        """
        try:
            uri = uri or _construct_uri_from_env() 
            self._client = MongoClient(uri, timeoutMS=5000)
            self._scaffdb  = self._client['scaffolding'] # scaffolding database
            self._profiles = self._scaffdb['profiles'] # profiles collection (table)
            self._sessions = self._scaffdb['sessions'] # sessions collection (table)
            self._session_logs = self._scaffdb['session_logs'] # logs collection (table)
            self._load_session_keys()
        except Exception as e:
            raise DatabaseConnectionException(f"Failed to establish connection with database or retrieve information: {e}") 
   

    def _load_session_keys(self) -> None:
        """Loads the session record index keys for validation."""
        self._session_keys = []
        for index in self._sessions.list_indexes():
            self._session_keys.extend(list(index['key'].keys()))
        self._session_keys.remove('_id')
        self._session_keys.remove('inserted_at')


    def _query_as_list(self, collection: Any, key: str, value: Any) -> List[Dict[Any, Any]]:
        """
        Queries the provied collection by a single index.

        Args:
            collection: Database collection (profiles or sessions)
            key: collection index key 
            value: index value 

        Returns:
            A list containing all documents that match the query.
        """
        return list(collection.find_one({ key: value }))
    

    def _add_insertion_timestamp(self, document: Dict[Any, Any]) -> None:
        """
        When inserting a new document into the database, adds the insertion time entry.

        Args:
            document: any python dictionary.
        Raises:
            IndexOverrideException: If the document was already inserted, the insertion timestamp should not be redefined.
        """
        if 'inserted_at' in document:
            raise IndexOverrideException("Document already contains a set unmodifiable 'inserted_at' index")

        document['inserted_at'] = datetime.utcnow().isoformat() 
        

    def insert_session_log(self, session_log: List[Dict[Any, Any]]) -> None:
        """
        Inserts a session log record after validating required keys.

        Args:
            session_log: A dictionary containing session log.
        Raises:
            MissingIndexException: If any required session log index is missing.
        """
        log = {'logs': session_log}

        self._add_insertion_timestamp(log)
        self._session_logs.insert_one(log)
    
    
    def get_latest_session_log(self) -> Optional[Dict[Any, Any]]:
        return self._sessions.find_one(sort=[('inserted_at', DESCENDING)])


    def insert_many_sessions(self, session_datas: List[Dict[Any, Any]]) -> None:
        """
        Inserts multiple session records into the database.

        Args:
            session_datas: List of dictionaries, each containing session data.
        """
        for data in session_datas: 
            self.insert_session(data)


    def insert_session(self, session_data: Dict[Any, Any]) -> None:
        """
        Inserts a single session record after validating required keys.

        Args:
            session_data: A dictionary containing session data.

        Raises:
            MissingIndexException: If any required session index is missing.
        """
        for key in self._session_keys:
            if key not in session_data:
                raise MissingIndexException(f"Session data is missing required index key '{key}'")
        
        self._add_insertion_timestamp(session_data)
        self._sessions.insert_one(session_data)
    

    def get_latest_session(self) -> Optional[Dict[Any, Any]]:
        """
        Retrieves the most recently inserted session.

        Returns:
            The latest session document or None if no session exists.
        """
        return self._sessions.find_one(sort=[('inserted_at', DESCENDING)])


    def get_session_by_id(self, session_id: str) -> Optional[Dict[Any, Any]]:
        """
        Retrieves a session by its unique session_id.

        Args:
            session_id: The session ID to look for.

        Returns:
            The matching session document or None if not found.
        """
        return self._sessions.find_one({ 'session_id': session_id })
    

    def get_sessions_by_mode(self, mode: Literal['experimental', 'demo']) -> List[Dict[Any, Any]]:
        """
        Fetches sessions by mode (experimental or demo).

        Args:
            mode: Either 'experimental' or 'demo'.

        Returns:
            A list of session documents matching the mode.
        """
        return self._query_as_list(self._sessions, 'mode', mode)


    def get_sessions_by_date(self, date: datetime) -> List[Dict[Any, Any]]:
        """
        Fetches all sessions that started on the given date.

        Args:
            date: The date to match (timezone-naive, UTC).

        Returns:
            A list of session documents with start_time matching the date.
        """
        date_str = date.strftime("%Y-%m-%d")
        return self._query_as_list(self._sessions, 'start_time', {"$regex": f"^{date_str}"})


    def get_sessions_by_agent_sequence(self, sequence: List[str]) -> List[Dict[Any, Any]]:
        """
        Fetches sessions matching a given agent execution sequence.

        Args:
            sequence: List of agent names in execution order.

        Returns:
            A list of session documents with matching agent_sequence.
        """
        return self._query_as_list(self._sessions, 'agent_sequence', sequence) 


    def insert_profile(self, username: str, password: str, profile: Profile) -> None:
        """
        Inserts a new user profile with a hashed password.

        Args:
            username: Unique identifier for the user.
            password: Plaintext password to hash and store.
            profile: Profile data as a Profile object.

        Raises:
            ProfileAlreadyExistsException: If the username already exists.
        """   
        # Query for the existing user profile
        if self._profiles.find_one({'username': username}):
            raise ProfileAlreadyExistsException(f"User profile with the name {username} already exists!")

        user_profile = UserProfile(username=username, 
                                      password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()), 
                                      profile=profile)
        
        self._profiles.insert_one(deep_asdict(user_profile))
    

    def query_profile(self, username: str, password: str) -> UserProfile:
        """
        Fetches and verifies a user profile by username and password.

        Args:
            username: The user's username.
            password: The user's plaintext password.

        Returns:
            A valid UserProfile object.

        Raises:
            ProfileNotFoundException: If username does not exist.
            FalsePasswordException: If password is incorrect.
        """
        quered_profile = self._profiles.find_one({'username': username})
        # Check whether the profile has been retrieved successfully
        if not quered_profile: 
            raise ProfileNotFoundException(f"User profile for {username} could not be found in the database")
       
        # Check whether the provided password matches the stored password
        if not bcrypt.checkpw(password.encode(), quered_profile['password']):
            raise FalsePasswordException(f"Invalid username or password")

        return UserProfile(username=quered_profile['username'], 
                              password=quered_profile['password'], 
                              profile=Profile(**quered_profile['profile']))


    def update_profile(self, profile: UserProfile) -> None: 
        """
        Placeholder for updating an existing user profile.

        Args:
            profile: A UserProfile object to update.
        """
        raise NotImplementedError("Profile update feature is not yet implemented")


    def ping(self) -> None:
        """
        Pings the MongoDB server to verify the connection.

        Raises:
            DatabaseConnectionException: If ping fails.
        """
        try:
            self._client.admin.command("ping")
            logger.info("Client pinged the server!")
        except Exception as e:
            raise DatabaseConnectionException("Failed to ping server with client: ", e)


if __name__ == "__main__":
    dbserv = MDBService()
    dbserv.ping()

