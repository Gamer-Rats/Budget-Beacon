from datetime import date
from fastapi import Request, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from app.utilities.flash import flash
from . import router, templates


@router.get("/expenses", response_class=HTMLResponse)
def expenses_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=""),
):
    repo = FinanceRepository(db)
    expenses, pagination = repo.list_expenses(user.id, q, page, limit)
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="expenses.html",
        context={
            "user": user,
            "expenses": expenses,
            "pagination": pagination,
            "q": q,
            "categories": categories,
            "editing_expense": None,
        },
    )


@router.post("/expenses")
def create_expense_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    title: str = Form(),
    amount: float = Form(),
    expense_date: date = Form(),
    notes: str = Form(default=""),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    repo.create_expense(user.id, title, amount, expense_date, notes, category_name)
    flash(request, "Expense created successfully")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/expenses/{expense_id}/edit", response_class=HTMLResponse)
def edit_expense_view(
    expense_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=""),
):
    repo = FinanceRepository(db)
    expense = repo.get_expense(expense_id, user.id)
    if not expense:
        flash(request, "Expense not found", "danger")
        return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)
    expenses, pagination = repo.list_expenses(user.id, q, page, limit)
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="expenses.html",
        context={
            "user": user,
            "expenses": expenses,
            "pagination": pagination,
            "q": q,
            "categories": categories,
            "editing_expense": expense,
        },
    )


@router.post("/expenses/{expense_id}/edit")
def update_expense_action(
    expense_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    title: str = Form(),
    amount: float = Form(),
    expense_date: date = Form(),
    notes: str = Form(default=""),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    expense = repo.get_expense(expense_id, user.id)
    if not expense:
        flash(request, "Expense not found", "danger")
    else:
        repo.update_expense(expense, title, amount, expense_date, notes, category_name)
        flash(request, "Expense updated successfully")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/expenses/{expense_id}/delete")
def delete_expense_action(expense_id: int, request: Request, user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    expense = repo.get_expense(expense_id, user.id)
    if not expense:
        flash(request, "Expense not found", "danger")
    else:
        repo.delete_expense(expense)
        flash(request, "Expense deleted successfully")
    return RedirectResponse(url=request.url_for("expenses_view"), status_code=status.HTTP_303_SEE_OTHER)
