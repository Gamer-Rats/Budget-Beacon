from fastapi.responses import RedirectResponse
from fastapi import Request, status
from . import router
from app.config import get_settings


@router.get("/logout")
async def logout(request: Request):
    secure_cookie = get_settings().env.lower() == "production"
    response = RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax" if not secure_cookie else "none",
        secure=secure_cookie,
    )
    return response
