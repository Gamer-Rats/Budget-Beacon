from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from . import router
from app.config import get_settings


@router.get("/", response_class=RedirectResponse)
async def index_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
):
    if user_logged_in:
        user = await get_current_user(request, db)
        if await is_admin(user):
            return RedirectResponse(url=request.url_for('admin_home_view'), status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url=request.url_for('user_home_view'), status_code=status.HTTP_303_SEE_OTHER)
    secure_cookie = get_settings().env.lower() == "production"
    response = RedirectResponse(url=request.url_for('login_view'), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax" if not secure_cookie else "none",
        secure=secure_cookie,
    )
    return response
