from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Expense, Tour
from ..schemas import ExpenseIn, ExpenseOut, ExpenseSummary
from ..security import get_current_admin

router = APIRouter(tags=["Expenses"], dependencies=[Depends(get_current_admin)])


def check_tour(db: Session, tour_id: int):
    if not db.get(Tour, tour_id):
        raise HTTPException(404, "Tour not found")


@router.post("/tours/{tour_id}/expenses", response_model=ExpenseOut, status_code=201)
def add_expense(tour_id: int, data: ExpenseIn, db: Session = Depends(get_db)):
    check_tour(db, tour_id)
    e = Expense(tour_id=tour_id, **data.model_dump())
    db.add(e)
    db.commit()
    return e


@router.get("/tours/{tour_id}/expenses", response_model=List[ExpenseOut])
def list_expenses(tour_id: int, db: Session = Depends(get_db)):
    check_tour(db, tour_id)
    return db.scalars(select(Expense).where(Expense.tour_id == tour_id)
                      .order_by(Expense.expense_date)).all()


@router.get("/tours/{tour_id}/expenses/summary", response_model=ExpenseSummary)
def expense_summary(tour_id: int, db: Session = Depends(get_db)):
    check_tour(db, tour_id)
    rows = db.execute(select(Expense.category, func.sum(Expense.amount))
                      .where(Expense.tour_id == tour_id).group_by(Expense.category)).all()
    by_cat = {c: float(t) for c, t in rows}
    return ExpenseSummary(tour_id=tour_id, by_category=by_cat, total=sum(by_cat.values()))


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    e = db.get(Expense, expense_id)
    if not e:
        raise HTTPException(404, "Expense not found")
    db.delete(e)
    db.commit()
