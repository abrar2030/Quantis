from fastapi import APIRouter, Depends, HTTPException

from ..middleware.auth import RoleChecker, validate_api_key
from ..schemas import User, UserCreate

router = APIRouter()
admin_role = RoleChecker("admin")

# Mock user database
users_db = {}
user_id_counter = 1


@router.post("/users/", response_model=User)
async def create_user(user: UserCreate, _: str = Depends(admin_role)):
    global user_id_counter

    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real app, you would hash the password here
    user_dict = user.dict()
    user_dict.pop("password")
    user_dict["id"] = user_id_counter
    user_dict["is_active"] = True

    users_db[user.email] = user_dict
    user_id_counter += 1

    return user_dict


@router.get("/users/", response_model=list[User])
async def read_users(_: str = Depends(admin_role)):
    return list(users_db.values())


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, _: str = Depends(validate_api_key)):
    for user in users_db.values():
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
