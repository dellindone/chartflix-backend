from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register')
def register():
    return {"message": "Register endpoint"}

@router.get('/login')
def login():
    return {"message": "Login endpoint"}