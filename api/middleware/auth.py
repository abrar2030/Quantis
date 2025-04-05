from fastapi import HTTPException, Depends  
from fastapi.security import APIKeyHeader  

security = APIKeyHeader(name="X-API-Key")  

async def validate_api_key(api_key: str = Depends(security)):  
    if api_key != os.getenv("API_SECRET"):  
        raise HTTPException(403, "Invalid API key")  
    return api_key  

class RoleChecker:  
    def __init__(self, required_role):  
        self.required_role = required_role  

    def __call__(self, user: dict = Depends(validate_api_key)):  
        if user["role"] != self.required_role:  
            raise HTTPException(403, "Insufficient permissions")  