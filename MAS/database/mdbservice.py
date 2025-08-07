import os, bcrypt
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from MAS.database.dtos import *
from datetime import datetime
from dataclasses import asdict

load_dotenv()
_uri = f"mongodb+srv://kristianschwarz:{os.environ['DB_PASSWORD']}@mas.oxzqvr2.mongodb.net/?retryWrites=true&w=majority&appName=MAS"

class DatabaseConnectionException(Exception): pass
class ProfileAlreadyExistsException(Exception): pass
class ProfileNotFoundException(Exception): pass
class FalsePasswordException(Exception): pass

class MDBService:
    def __init__(self) -> None:
        try:
            self._client = MongoClient(_uri, timeoutMS=5000)
            self._scaffdb  = self._client['scaffolding']
            self._profiles = self._scaffdb['profiles']
            self._sessions = self._scaffdb['sessions']
        except Exception as e:
            raise DatabaseConnectionException(f"Failed to connect to the database: {e}") 
    

    def insert_session(self, session_data) -> None:
        self._sessions.insert_one(session_data)


    def get_sessions_by_date(self, date: datetime) -> List[Session]:
        date_str = date.strftime("%Y-%m-%d")
        cursor = self._sessions.find({
            "start_time": {"$regex": f"^{date_str}"}
        })
        return [self._doc_to_session(doc) for doc in cursor]


    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        doc = self._sessions.find_one({ "session_id": session_id })
        return self._doc_to_session(doc) if doc else None


    def _doc_to_session(self, doc: dict) -> Session:
        doc.pop("_id", None)
        return Session(**doc)


    def insert_profile(self, username: str, password: str, profile: Profile) -> None:
        """
        Inserts a new user profile into the database.
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
        Retrieves the user profile from the database.
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
        pass


    def ping(self) -> None:
        """
        Test whether the server is reachable (for debug purposes).
        """
        try:
            self._client.admin.command("ping")
            print("Client pinged the server!")
        except Exception as e:
            raise DatabaseConnectionException("Failed to ping server with client: ", e)


if __name__ == "__main__":
    dbserv = MDBService()
    dbserv.ping()

