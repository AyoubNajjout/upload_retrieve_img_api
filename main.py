import base64

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/temp_db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(50))


class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), ForeignKey("users.username"))
    img_decoded = Column(String(100))


Base.metadata.create_all(bind=engine)


class UserRegister(BaseModel):
    username: str
    password: str
    confirmation: str
    email: str


@app.post("/api/v1/auth/register")
def create_user(user: UserRegister):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(user.username == User.username).first()
        if existing_user:
            raise HTTPException(status_code=403, detail=f"this username {user.username} is already existing ! ")
        if user.password == user.confirmation:
            db_user = User(username=user.username, email=user.email, password=user.password)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return "user registered successfully"
        else:
            raise HTTPException(status_code=403, detail="passwords dont match !")
    finally:
        db.close()


@app.post("/api/v1/auth/{username}/add-picture")
async def add_profile_picture(username, file: UploadFile = File(...)):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(username == User.username).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with username {username} not found")
        img_binary = await file.read()
        img_encoded = base64.b64encode(img_binary)
        db_user = UserProfile(user=username, img_decoded=img_encoded)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "Profile picture added successfully"}
    finally:
        db.close()


@app.get("/api/v1/auth/{username}/get-picture")
def get_user_profile(username):
    db = SessionLocal()
    try:
        existing_user = db.query(UserProfile).filter(username == UserProfile.user).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with username {username} not found")
        img_encoded = existing_user.img_decoded
        img_binary = base64.b64decode(img_encoded)
        return Response(content=img_binary, media_type="image/jpeg")
    finally:
        db.close()
