from pydantic import BaseModel

class MoveRequest(BaseModel):
    session_id : str
    action : str