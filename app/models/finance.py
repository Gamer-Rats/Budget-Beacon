from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class ExpenseCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(index=True)

    user: "User" = Relationship(back_populates="categories")
    expenses: list["Expense"] = Relationship(back_populates="category")
    subscriptions: list["Subscription"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="expensecategory.id")
    title: str = Field(max_length=255)
    amount: float
    expense_date: date
    notes: str = ""

    user: "User" = Relationship(back_populates="expenses")
    category: Optional[ExpenseCategory] = Relationship(back_populates="expenses")


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="expensecategory.id")
    name: str = Field(max_length=255)
    amount: float
    billing_cycle: str = "monthly"
    next_payment_date: date
    active: bool = True

    user: "User" = Relationship(back_populates="subscriptions")
    category: Optional[ExpenseCategory] = Relationship(back_populates="subscriptions")


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="expensecategory.id")
    month: str = Field(index=True)
    limit_amount: float

    user: "User" = Relationship(back_populates="budgets")
    category: Optional[ExpenseCategory] = Relationship(back_populates="budgets")
