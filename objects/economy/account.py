from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging

from sqlalchemy import Column, Boolean, Integer, BigInteger, DateTime

from objects.base import Base


class EconomyAccount(Base):
    __tablename__ = 'economy_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    balance = Column(BigInteger)
    income = Column(BigInteger)
    enabled = Column(Boolean)
    lastclaim = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<User id={0.id}, enabled={0.enabled}, balance={0.balance}>".format(self)

    @staticmethod
    def get_all_economy_accounts(session):
        return session.query(EconomyAccount).all()

    @staticmethod
    def get_top_economy_accounts(session, number=20):
        return session.query(EconomyAccount).order_by(EconomyAccount.balance.desc()).all()[:number]

    @staticmethod
    def get_economy_account(user, session, create_if_not_exists=True) -> EconomyAccount:
        user_id = user.id
        result = session.query(EconomyAccount).filter_by(user_id=user_id).first()
        if result is None and create_if_not_exists:
            return EconomyAccount.create_economy_account(user, session, not user.bot)
        return result

    @staticmethod
    def create_economy_account(user, session, enabled, commit_on_execution=True):
        user_id = user.id
        new_account = EconomyAccount(
            user_id = user_id,
            balance = 100000,
            income = 20000,
            enabled = enabled,
            lastclaim = None,
        )
        session.add(new_account)
        if commit_on_execution:
            session.commit()
        return new_account

    def has_balance(self, amount, raw=False):
        if not raw:
            amount *= 10000
        return amount <= self.balance

    def get_balance(self):
        return self.balance / 10000 # Convert to database-friendly format

    def get_income(self):
        return self.income / 10000 # Convert to database-friendly format

    def dispense_income(self, session):
        if(self.lastclaim == None):
            self.lastclaim = datetime.now()
            self.balance += self.income
            self.claimavailable = False
            session.commit()
            return 0
        timediff = self.lastclaim - datetime.now()
        if(timediff.days>=1):
            self.balance += self.income
            self.lastclaim = datetime.now()
            session.commit()
            return 0
        else:
            return 1

    def resetincomeclaim(self, session):
        self.claimavailable = True
        session.commit()
        return
