from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import os
from pathlib import Path

from database import SessionLocal, engine, Base
from models import User, Alert, Sensor
from schemas import (
    UserCreate, UserResponse, Token, AlertCreate, AlertResponse,
    AlertResolve, SensorResponse, SensorCreate
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Forest Protection IoT Dashboard API")

# CORS configuration
# Get frontend URL from environment variable, default to allow all for development
FRONTEND_URL = os.getenv("FRONTEND_URL") or os.getenv("CORS_ORIGIN") or "*"

# Build CORS origins list
if FRONTEND_URL == "*":
    cors_origins = ["*"]
else:
    # Allow specific frontend URL
    cors_origins = [FRONTEND_URL]
    # Also allow Vercel preview deployments
    if "vercel.app" in FRONTEND_URL:
        # Allow the exact domain and any subdomain
        cors_origins.append("https://*.vercel.app")

# Log CORS configuration for debugging
print(f"CORS Origins configured: {cors_origins}")
print(f"FRONTEND_URL from env: {FRONTEND_URL}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Auth endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Sensor endpoints
@app.post("/api/sensors", response_model=SensorResponse)
async def create_sensor(sensor_data: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_data.sensor_id).first()
    if db_sensor:
        raise HTTPException(status_code=400, detail="Sensor ID already exists")
    
    db_sensor = Sensor(
        sensor_id=sensor_data.sensor_id,
        sensor_name=sensor_data.sensor_name,
        latitude=sensor_data.latitude,
        longitude=sensor_data.longitude
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@app.get("/api/sensors", response_model=List[SensorResponse])
async def get_sensors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sensors = db.query(Sensor).all()
    return sensors

# Alert endpoints - for Node-RED (no auth required)
@app.post("/api/alerts", response_model=AlertResponse)
async def create_alert(alert_data: AlertCreate, db: Session = Depends(get_db)):
    # Check if sensor exists, if not create it
    sensor = db.query(Sensor).filter(Sensor.sensor_id == alert_data.sensor_id).first()
    if not sensor:
        sensor = Sensor(
            sensor_id=alert_data.sensor_id,
            sensor_name=alert_data.sensor_name or f"Sensor {alert_data.sensor_id}",
            latitude=0.0,
            longitude=0.0
        )
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
    
    # Create alert
    db_alert = Alert(
        sensor_id=alert_data.sensor_id,
        sensor_name=alert_data.sensor_name or sensor.sensor_name,
        alert_time=alert_data.alert_time or datetime.utcnow(),
        resolved=False
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    alerts = query.order_by(desc(Alert.alert_time)).all()
    return alerts

@app.get("/api/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.post("/api/alerts/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    threat_type: str = Form(...),
    details: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.resolved:
        raise HTTPException(status_code=400, detail="Alert already resolved")
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{alert_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update alert
    alert.resolved = True
    alert.resolved_by = current_user.id
    alert.resolved_at = datetime.utcnow()
    alert.threat_type = threat_type
    alert.resolution_details = details
    alert.attachment_path = str(file_path)
    
    db.commit()
    db.refresh(alert)
    return alert

@app.get("/api/sensors/{sensor_id}/status")
async def get_sensor_status(sensor_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if sensor has unresolved alerts
    unresolved_alert = db.query(Alert).filter(
        Alert.sensor_id == sensor_id,
        Alert.resolved == False
    ).order_by(desc(Alert.alert_time)).first()
    
    return {
        "sensor_id": sensor_id,
        "status": "red" if unresolved_alert else "green",
        "has_unresolved_alert": unresolved_alert is not None
    }

@app.get("/api/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sensors = db.query(Sensor).all()
    sensor_statuses = []
    
    for sensor in sensors:
        unresolved_alert = db.query(Alert).filter(
            Alert.sensor_id == sensor.sensor_id,
            Alert.resolved == False
        ).order_by(desc(Alert.alert_time)).first()
        
        sensor_statuses.append({
            "sensor_id": sensor.sensor_id,
            "sensor_name": sensor.sensor_name,
            "latitude": sensor.latitude,
            "longitude": sensor.longitude,
            "status": "red" if unresolved_alert else "green",
            "last_alert_time": unresolved_alert.alert_time.isoformat() if unresolved_alert else None
        })
    
    total_alerts = db.query(Alert).count()
    unresolved_count = db.query(Alert).filter(Alert.resolved == False).count()
    resolved_count = db.query(Alert).filter(Alert.resolved == True).count()
    
    return {
        "sensors": sensor_statuses,
        "statistics": {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_count,
            "resolved_alerts": resolved_count,
            "total_sensors": len(sensors)
        }
    }

@app.get("/")
@app.head("/")
async def root():
    return {"message": "Forest Protection IoT Dashboard API", "status": "ok"}

@app.get("/health")
@app.head("/health")
async def health_check():
    """Health check endpoint for Render and other monitoring services"""
    return {"status": "healthy", "service": "Forest Protection IoT Dashboard API"}

