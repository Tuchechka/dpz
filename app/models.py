"""Доменна модель -- один рядок датасету Dallas Budget vs Actual."""
from typing import Optional

from pydantic import BaseModel


class BudgetRecord(BaseModel):
    """Один рядок з датасету: бюджетна стаття одного відділу за рік."""

    fiscal_year: int
    department: str
    account_code: str
    account_description: str
    budget_amount: float
    actual_amount: float
    variance: Optional[float] = None

    def __str__(self) -> str:
        return (
            f"[{self.fiscal_year}] {self.department} | {self.account_description}: "
            f"budget=${self.budget_amount:,.2f} actual=${self.actual_amount:,.2f} "
            f"variance=${self.variance:,.2f}"
        )
