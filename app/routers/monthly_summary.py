from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from . import router, templates


@router.get("/monthly-summary", response_class=HTMLResponse)
def monthly_summary_view(request: Request, user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    summary = repo.get_monthly_summary(user)

    return templates.TemplateResponse(
        request=request,
        name="monthly_summary.html",
        context={
            "user": user,
            "summary": summary,
        },
    )