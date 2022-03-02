from __future__ import annotations
from binascii import Incomplete

from datetime import datetime
import logging

from sqlalchemy import Column, Boolean, Integer, BigInteger, DateTime, UniqueConstraint, and_

from objects.base import Base


class EconomyAccount(Base):
    __tablename__ = 'economy_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)            # Discord user id
    guild_id = Column(BigInteger)           # Discord server id
    balance = Column(BigInteger)
    income = Column(BigInteger)
    enabled = Column(Boolean)
    lastclaim = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Pair (user_id, guild_id) should be unique per entry
    __table_args__ = (
        UniqueConstraint('user_id', 'guild_id', name='_user_guild_uc'),
    )

    def __repr__(self):
        return "<User id={0.id}, enabled={0.enabled}, balance={0.balance}>".format(self)

    @staticmethod
    def get_economy_account(member, session, create_if_not_exists=True) -> EconomyAccount:
        user_id = member.id
        guild_id = member.guild.id

        # Search for unique user_id + guild_id combination
        result = session.query(EconomyAccount).filter(
            and_(
                EconomyAccount.user_id == user_id,
                EconomyAccount.guild_id == guild_id
            )
        ).first()

        if result is None and create_if_not_exists:
            return EconomyAccount.create_economy_account(member, session, not member.bot)

        return result

    @staticmethod
    def create_economy_account(member, session, enabled, commit_on_execution=True):
        # Get member's details
        user_id = member.id
        guild_id = member.guild.id

        # Initialize new account
        new_account = EconomyAccount(
            user_id = user_id,
            guild_id = guild_id,
            balance = 100000,
            income = 20000,
            enabled = enabled,
            lastclaim = None,
        )

        # Commit new account to DB
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
        self.lastclaim = None
        session.commit()
        return
