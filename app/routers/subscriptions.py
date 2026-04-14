from datetime import date
from fastapi import Request, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.finance import FinanceRepository
from app.utilities.flash import flash
from . import router, templates


def _parse_optional_float(value: str | None) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _parse_optional_date(value: str | None) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@router.get("/subscriptions", response_class=HTMLResponse)
def subscriptions_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, le=100),
    q: str = Query(default=""),
    category_name: str = Query(default=""),
    min_amount: str = Query(default=""),
    max_amount: str = Query(default=""),
    start_date: str = Query(default=""),
    end_date: str = Query(default=""),
    active: str = Query(default=""),
):
    min_amount_value = _parse_optional_float(min_amount)
    max_amount_value = _parse_optional_float(max_amount)
    start_date_value = _parse_optional_date(start_date)
    end_date_value = _parse_optional_date(end_date)

    repo = FinanceRepository(db)
    subscriptions, pagination = repo.list_subscriptions(
        user.id,
        q=q,
        category_name=category_name,
        min_amount=min_amount_value,
        max_amount=max_amount_value,
        start_date=start_date_value,
        end_date=end_date_value,
        active=active,
        page=page,
        limit=limit,
    )
    categories = repo.get_categories(user.id)
    monthly_total = sum(float(subscription.amount) for subscription in subscriptions)
    yearly_total = monthly_total * 12

    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "user": user,
            "subscriptions": subscriptions,
            "pagination": pagination,
            "q": q,
            "category_name": category_name,
            "min_amount": min_amount_value,
            "max_amount": max_amount_value,
            "start_date": start_date_value,
            "end_date": end_date_value,
            "active": active,
            "categories": categories,
            "monthly_total": monthly_total,
            "yearly_total": yearly_total,
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
    category_name: str = Query(default=""),
    min_amount: str = Query(default=""),
    max_amount: str = Query(default=""),
    start_date: str = Query(default=""),
    end_date: str = Query(default=""),
    active: str = Query(default=""),
):
    min_amount_value = _parse_optional_float(min_amount)
    max_amount_value = _parse_optional_float(max_amount)
    start_date_value = _parse_optional_date(start_date)
    end_date_value = _parse_optional_date(end_date)

    repo = FinanceRepository(db)
    subscription = repo.get_subscription(subscription_id, user.id)
    if not subscription:
        flash(request, "Subscription not found", "danger")
        return RedirectResponse(url=request.url_for("subscriptions_view"), status_code=status.HTTP_303_SEE_OTHER)
    subscriptions, pagination = repo.list_subscriptions(
        user.id,
        q=q,
        category_name=category_name,
        min_amount=min_amount_value,
        max_amount=max_amount_value,
        start_date=start_date_value,
        end_date=end_date_value,
        active=active,
        page=page,
        limit=limit,
    )
    categories = repo.get_categories(user.id)
    monthly_total = sum(float(item.amount) for item in subscriptions)
    yearly_total = monthly_total * 12
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "user": user,
            "subscriptions": subscriptions,
            "pagination": pagination,
            "q": q,
            "category_name": category_name,
            "min_amount": min_amount_value,
            "max_amount": max_amount_value,
            "start_date": start_date_value,
            "end_date": end_date_value,
            "active": active,
            "categories": categories,
            "monthly_total": monthly_total,
            "yearly_total": yearly_total,
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
