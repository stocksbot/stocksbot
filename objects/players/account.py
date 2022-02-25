from __future__ import annotations

from datetime import datetime
import logging

from sqlalchemy import Column, Boolean, Integer, BigInteger, DateTime

from objects.base import Base


class PlayerAccount(Base):
    __tablename__ = 'economy_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    balance = Column(BigInteger)
    enabled = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<User id={0.id}, enabled={0.enabled}, balance={0.balance}>".format(self)

    @staticmethod
    def get_all_economy_accounts(session):
        return session.query(PlayerAccount).all()

    @staticmethod
    def get_top_economy_accounts(session, number=20):
        return session.query(PlayerAccount).order_by(PlayerAccount.balance.desc()).all()[:number]

    @staticmethod
    def get_economy_account(user, session, create_if_not_exists=True) -> PlayerAccount:
        user_id = user.id
        result = session.query(PlayerAccount).filter_by(user_id=user_id).first()
        if result is None and create_if_not_exists:
            return PlayerAccount.create_economy_account(user, session, not user.bot)
        return result

    @staticmethod
    def create_economy_account(user, session, enabled, commit_on_execution=True):
        user_id = user.id
        new_account = PlayerAccount(
            user_id = user_id,
            balance = 100000,
            enabled = enabled,
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
