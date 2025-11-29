from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.models.auth import User
from app.utils.auth import verify_password, get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # For now, auto-create a company (in real app, user would select or create)
    from app.models.auth import Company
    import uuid
    
    # Create company
    company = Company(
        id=uuid.uuid4(),
        name=f"{user_data.full_name}'s Company",
        is_active=True
    )
    db.add(company)
    db.flush()
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=uuid.uuid4(),
        company_id=company.id,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(new_user)
    db.flush() # Generate ID without committing transaction
    db.refresh(new_user)
    
    # Audit log
    from app.utils.audit import log_audit
    log_audit(
        db=db,
        company_id=company.id,
        user_id=new_user.id,
        entity_type="USER",
        entity_id=new_user.id,
        action="CREATE",
        changes={"email": new_user.email, "role": new_user.role}
    )
    db.commit()
    
    return new_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "company_id": str(user.company_id)},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
