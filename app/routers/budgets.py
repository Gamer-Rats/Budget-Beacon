from typing import Optional

from fastapi import Request, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from app.utilities.flash import flash
from . import router, templates


def _parse_optional_float(value: Optional[str]) -> Optional[float]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


@router.get("/budgets", response_class=HTMLResponse)
def budgets_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    month: str = Query(default=""),
    category_name: str = Query(default=""),
    min_amount: str = Query(default=""),
    max_amount: str = Query(default=""),
):
    min_amount_value = _parse_optional_float(min_amount)
    max_amount_value = _parse_optional_float(max_amount)

    repo = FinanceRepository(db)
    budgets, pagination = repo.list_budgets(
        user.id,
        month=month,
        category_name=category_name,
        min_amount=min_amount_value,
        max_amount=max_amount_value,
        page=page,
        limit=limit,
    )
    budget_meta = {}
    budget_alerts = []
    for budget in budgets:
        spent = repo.get_budget_spent(user.id, budget.month, budget.category_id)
        percent = spent / budget.limit_amount if budget.limit_amount else 0
        status = "normal"
        if percent > 1:
            status = "alert"
            budget_alerts.append(
                {
                    "message": f"You exceeded your {budget.category.name if budget.category else 'Uncategorized'} budget!",
                    "level": "danger",
                }
            )
        elif percent > 0.8:
            status = "warning"
            budget_alerts.append(
                {
                    "message": f"You are nearing your {budget.category.name if budget.category else 'Uncategorized'} budget.",
                    "level": "warning",
                }
            )
        budget_meta[budget.id] = {
            "spent": spent,
            "percent": percent,
            "status": status,
        }
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
            "min_amount": min_amount_value,
            "max_amount": max_amount_value,
            "categories": categories,
            "editing_budget": None,
            "budget_meta": budget_meta,
            "budget_alerts": budget_alerts,
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
    budget_meta = {}
    budget_alerts = []
    for item in budgets:
        spent = repo.get_budget_spent(user.id, item.month, item.category_id)
        percent = spent / item.limit_amount if item.limit_amount else 0
        status = "normal"
        if percent > 1:
            status = "alert"
            budget_alerts.append(
                {
                    "message": f"You exceeded your {item.category.name if item.category else 'Uncategorized'} budget!",
                    "level": "danger",
                }
            )
        elif percent > 0.8:
            status = "warning"
            budget_alerts.append(
                {
                    "message": f"You are nearing your {item.category.name if item.category else 'Uncategorized'} budget.",
                    "level": "warning",
                }
            )
        budget_meta[item.id] = {
            "spent": spent,
            "percent": percent,
            "status": status,
        }
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
            "budget_meta": budget_meta,
            "budget_alerts": budget_alerts,
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
