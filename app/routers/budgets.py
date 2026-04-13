from fastapi import Request, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from app.utilities.flash import flash
from . import router, templates


@router.get("/budgets", response_class=HTMLResponse)
def budgets_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    month: str = Query(default=""),
    category_name: str = Query(default=""),
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
):
    repo = FinanceRepository(db)
    budgets, pagination = repo.list_budgets(
        user.id,
        month=month,
        category_name=category_name,
        min_amount=min_amount,
        max_amount=max_amount,
        page=page,
        limit=limit,
    )
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="budgets.html",
        context={
            "user": user,
            "budgets": budgets,
            "pagination": pagination,
            "month": month,
            "category_name": category_name,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "categories": categories,
            "editing_budget": None,
        },
    )


@router.post("/budgets")
def create_budget_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    month: str = Form(),
    limit_amount: float = Form(),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    repo.create_budget(user.id, month, limit_amount, category_name)
    flash(request, "Budget created successfully")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/budgets/{budget_id}/edit", response_class=HTMLResponse)
def edit_budget_view(
    budget_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    month: str = Query(default=""),
):
    repo = FinanceRepository(db)
    budget = repo.get_budget(budget_id, user.id)
    if not budget:
        flash(request, "Budget not found", "danger")
        return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)
    budgets, pagination = repo.list_budgets(user.id, month, page, limit)
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="budgets.html",
        context={
            "user": user,
            "budgets": budgets,
            "pagination": pagination,
            "month": month,
            "categories": categories,
            "editing_budget": budget,
        },
    )


@router.post("/budgets/{budget_id}/edit")
def update_budget_action(
    budget_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    month: str = Form(),
    limit_amount: float = Form(),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    budget = repo.get_budget(budget_id, user.id)
    if not budget:
        flash(request, "Budget not found", "danger")
    else:
        repo.update_budget(budget, month, limit_amount, category_name)
        flash(request, "Budget updated successfully")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/budgets/{budget_id}/delete")
def delete_budget_action(budget_id: int, request: Request, user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    budget = repo.get_budget(budget_id, user.id)
    if not budget:
        flash(request, "Budget not found", "danger")
    else:
        repo.delete_budget(budget)
        flash(request, "Budget deleted successfully")
    return RedirectResponse(url=request.url_for("budgets_view"), status_code=status.HTTP_303_SEE_OTHER)
