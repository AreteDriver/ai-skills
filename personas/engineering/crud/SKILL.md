---
name: crud
description: CRUD Boilerplate Generator
lifecycle: experimental
---

# /crud - CRUD Boilerplate Generator

Generate Create, Read, Update, Delete boilerplate from models.

## Usage
```
/crud User                       # Generate CRUD for User model
/crud --model "id:int, name:str" # Generate from schema
/crud --framework fastapi        # FastAPI endpoints
/crud --framework sqlalchemy     # SQLAlchemy repository
```

## What This Skill Does

1. **Parse Model** - Extract fields, types, relationships
2. **Generate Model** - Pydantic/dataclass/SQLAlchemy
3. **Create Repository** - Data access layer
4. **Add Endpoints** - REST API routes
5. **Write Tests** - CRUD operation tests

## FastAPI CRUD

### Model
```python
# models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

### Schemas
```python
# schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Repository
```python
# repositories/user.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User
from schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        user = self.get(user_id)
        if not user:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
```

### Endpoints
```python
# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from repositories.user import UserRepository
from schemas.user import UserCreate, UserUpdate, UserResponse
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])

def get_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    """Create a new user."""
    if repo.get_by_username(data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return repo.create(data)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    """Get a user by ID."""
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    repo: UserRepository = Depends(get_repo)
):
    """List all users."""
    return repo.get_all(skip=skip, limit=limit)

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    repo: UserRepository = Depends(get_repo)
):
    """Update a user."""
    user = repo.update(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    """Delete a user."""
    if not repo.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")
```

### Tests
```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_get_user(client: TestClient, sample_user):
    response = client.get(f"/users/{sample_user.id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_user.id

def test_list_users(client: TestClient, sample_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_update_user(client: TestClient, sample_user):
    response = client.patch(f"/users/{sample_user.id}", json={
        "username": "updated"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "updated"

def test_delete_user(client: TestClient, sample_user):
    response = client.delete(f"/users/{sample_user.id}")
    assert response.status_code == 204
```

## Instructions for Claude

When /crud is invoked:

1. **Parse model** - Fields, types, relationships
2. **Generate model** - SQLAlchemy or dataclass
3. **Create schemas** - Pydantic for API
4. **Build repository** - Data access methods
5. **Add endpoints** - REST routes
6. **Include validation** - Input validation, error handling
7. **Write tests** - All CRUD operations
8. **Consider relations** - Foreign keys, nested objects
