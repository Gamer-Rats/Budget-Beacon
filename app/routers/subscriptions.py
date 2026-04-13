from datetime import date
from fastapi import Request, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from app.utilities.flash import flash
from . import router, templates


@router.get("/subscriptions", response_class=HTMLResponse)
def subscriptions_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=""),
):
    repo = FinanceRepository(db)
    subscriptions, pagination = repo.list_subscriptions(user.id, q, page, limit)
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "user": user,
            "subscriptions": subscriptions,
            "pagination": pagination,
            "q": q,
            "categories": categories,
            "editing_subscription": None,
        },
    )


@router.post("/subscriptions")
def create_subscription_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    name: str = Form(),
    amount: float = Form(),
    billing_cycle: str = Form(),
    next_payment_date: date = Form(),
    active: str = Form(default="true"),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    repo.create_subscription(user.id, name, amount, billing_cycle, next_payment_date, active == "true", category_name)
    flash(request, "Subscription created successfully")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/subscriptions/{subscription_id}/edit", response_class=HTMLResponse)
def edit_subscription_view(
    subscription_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=""),
):
    repo = FinanceRepository(db)
    subscription = repo.get_subscription(subscription_id, user.id)
    if not subscription:
        flash(request, "Subscription not found", "danger")
        return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)
    subscriptions, pagination = repo.list_subscriptions(user.id, q, page, limit)
    categories = repo.get_categories(user.id)
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "user": user,
            "subscriptions": subscriptions,
            "pagination": pagination,
            "q": q,
            "categories": categories,
            "editing_subscription": subscription,
        },
    )


@router.post("/subscriptions/{subscription_id}/edit")
def update_subscription_action(
    subscription_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
    name: str = Form(),
    amount: float = Form(),
    billing_cycle: str = Form(),
    next_payment_date: date = Form(),
    active: str = Form(default="true"),
    category_name: str = Form(default=""),
):
    repo = FinanceRepository(db)
    subscription = repo.get_subscription(subscription_id, user.id)
    if not subscription:
        flash(request, "Subscription not found", "danger")
    else:
        repo.update_subscription(subscription, name, amount, billing_cycle, next_payment_date, active == "true", category_name)
        flash(request, "Subscription updated successfully")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/subscriptions/{subscription_id}/delete")
def delete_subscription_action(subscription_id: int, request: Request, user: AuthDep, db: SessionDep):
    repo = FinanceRepository(db)
    subscription = repo.get_subscription(subscription_id, user.id)
    if not subscription:
        flash(request, "Subscription not found", "danger")
    else:
        repo.delete_subscription(subscription)
        flash(request, "Subscription deleted successfully")
    return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)
