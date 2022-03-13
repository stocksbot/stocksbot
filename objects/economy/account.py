from __future__ import annotations
from binascii import Incomplete

from datetime import datetime, timedelta
import logging
import nextcord
from nextcord import Member
from typing import Optional, Union

from sqlalchemy import Column, Boolean, Float, Integer, BigInteger, DateTime, UniqueConstraint, and_
from sqlalchemy.orm import Session

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
    def get_economy_account(member:Member, session:Session, create_if_not_exists=True) -> Optional[EconomyAccount]:
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
    def create_economy_account(member, session:Session, enabled, commit_on_execution=True):
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
    
    @staticmethod
    def delete_economy_account(member, session:Session):
        user_id = member.id
        guild_id = member.guild.id

        # Search for unique user_id + guild_id combination
        result = session.query(EconomyAccount).filter(
            and_(
                EconomyAccount.user_id == user_id,
                EconomyAccount.guild_id == guild_id
            )
        ).delete()

        return result

    def has_balance(self, amount, raw=False):
        if not raw:
            amount *= 10000
        return amount <= self.balance

    def get_balance(self):
        return self.balance / 10000 # Convert to database-friendly format

    def get_income(self):
        return self.income / 10000 # Convert to database-friendly format

    def increasebalance(self, session:Session, amount, raw=False, commit=True):
        if(raw):
            self.balance += amount
        else:
            self.balance += round(amount*10000)
        if(commit):
            session.commit()

    def dispense_income(self, session:Session):
        """Returns 0 on successful dispense, otherwise returns datetime when claim will be ready again"""
        if(self.lastclaim == None):
            self.lastclaim = datetime.now()
            self.balance += self.income
            self.claimavailable = False
            session.commit()
            return 0
        timediff = datetime.now() - self.lastclaim
        if(timediff.days>=1):
            self.balance += self.income
            self.lastclaim = datetime.now()
            session.commit()
            return 0
        else:
            return self.lastclaim + timedelta(days=1)

    def resetincomeclaim(self, session:Session):
        self.lastclaim = None
        session.commit()
        return

    def updateincome(self, session, newincome):
        self.income = int(newincome*10000)
        session.commit()
        return