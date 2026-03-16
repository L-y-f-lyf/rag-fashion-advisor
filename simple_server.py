# 最简化的 FastAPI 应用 - 只保留认证功能
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import hashlib
import uuid
import os
import logging
import traceback

# 配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SECRET_KEY = "fastapi-secret-2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# 数据库
DATABASE_URL = "sqlite:///./rag_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建表
Base.metadata.create_all(bind=engine)

# FastAPI 应用
app = FastAPI(title="RAG 智能问答系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 工具函数
def hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = uuid.uuid4().hex
    pwd_hash = hashlib.sha256(f"{salt}{password}{salt}".encode()).hexdigest()
    return f"sha256${salt}${pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        salt = parts[1]
        return hash_password(plain_password, salt) == hashed_password
    except:
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exc = HTTPException(status_code=401, detail="认证失败", headers={"WWW-Authenticate": "Bearer"})
    payload = decode_token(token)
    if not payload:
        raise credentials_exc
    username = payload.get("sub")
    if not username:
        raise credentials_exc
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exc
    return user

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    error_detail = f"{type(exc).__name__}: {str(exc)}"
    logger.error(f"500 错误：{error_detail}")
    logger.error(traceback.format_exc())
    print(f"500 错误：{error_detail}")
    print(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.warning(f"{exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# 路由
@app.post("/api/auth/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    """用户注册"""
    logger.info(f"注册请求：username={username}")
    print(f"注册请求：username={username}")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed = hash_password(password)
    logger.info(f"密码哈希：{hashed[:30]}...")
    print(f"密码哈希：{hashed[:30]}...")

    new_user = User(username=username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"用户创建成功：id={new_user.id}")
    print(f"用户创建成功：id={new_user.id}")
    return {"id": new_user.id, "username": new_user.username, "created_at": new_user.created_at}

@app.post("/api/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    """用户登录"""
    logger.info(f"登录请求：username={username}")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(data={"sub": user.username})
    logger.info("登录成功")
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "RAG API 运行中", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("启动服务器 http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
