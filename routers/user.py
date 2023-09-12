import sys
sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, status, APIRouter, Request, Form
import models
from sqlalchemy.orm import Session
from database import SessionLocal

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routers.auth import get_current_user, authenticate_user, get_password_hash

router = APIRouter(
    prefix="/user",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def change_password(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("manage.html", {"request": request, "user": user})

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(request: Request, password0: str = Form(...), password1: str = Form(...), 
                          password2: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    verify_user_password = authenticate_user(user_model.username, password0, db)
    if verify_user_password == False:
        msg = "Incorect password"
        return templates.TemplateResponse("manage.html", {"request": request, "user": user, "msg2": msg})

    if password1 != password2:
        msg = "New password are not the same"
        return templates.TemplateResponse("manage.html", {"request": request, "user": user, "msg2": msg})

    new_password = get_password_hash(password1)
    user_model.hashed_password = new_password
    
    db.add(user_model)
    db.commit()

    msg = "Successfuly Changed"
    return templates.TemplateResponse("manage.html", {"request": request, "user": user, "msg2": msg})