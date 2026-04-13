from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from . import router, api_router, templates


@router.get("/reports", response_class=HTMLResponse)
def reports_view(request: Request, user: AuthDep, db: SessionDep):
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "user": user,
        },
    )


@api_router.get("/expense-stats")
def expense_stats(user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    return repo.expense_breakdown(user.id)


@api_router.get("/subscription-stats")
def subscription_stats(user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    return repo.subscription_breakdown(user.id)
