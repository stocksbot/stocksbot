from __future__ import annotations
from binascii import Incomplete

from datetime import datetime, timedelta
import logging
import nextcord
from nextcord import Member
from typing import Optional, Union

from sqlalchemy import Column, Boolean, Float, Integer, BigInteger, DateTime, UniqueConstraint, String, and_
from sqlalchemy.orm import Session

from objects.base import Base

from objects.economy.account import EconomyAccount

class LocalLeaderboard(Base):
    __tablename__ = 'local_leaderboard'

    id = Column(Integer, primary_key=True)  # Table ID
    guild_id = Column(BigInteger)           # Discord server id
    top_users_id = Column(String)           # List of Discord user ids represented in string
    top_users_name = Column(String)         # List of Discord user names represented in string
    top_users_tag = Column(String)          # List of Discord user tags represented in string
    points = Column(String)                 # List of Points / Balances represented in string
    size = Column(Integer)                  # Size of Leaderboard

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return "<table id={0.id}, guild={0.guild_id}, top_users=[{0.top_users_name}]>".format(self)

    @staticmethod
    def get_local_leaderboard(member:Member, session:Session, create_if_not_exists=True) -> Optional[LocalLeaderboard]:
        guild_id = member.guild.id

        # Search for guild_id
        result = session.query(LocalLeaderboard).filter(
            LocalLeaderboard.guild_id == guild_id
        ).first()

        if result is None and create_if_not_exists:
            return LocalLeaderboard.create_local_leaderboard(member, session)

        return result

    @staticmethod
    def create_local_leaderboard(member:Member, session:Session, size = 10):
        new_top_users_id = [0]*size
        new_top_users_name = ["---"]*size
        new_top_users_tag = [0]*size
        new_points = [0]*size

        new_localboard = LocalLeaderboard(
            guild_id = member.guild.id,
            top_users_id = ' '.join([str(item) for item in new_top_users_id]),
            top_users_name = ' '.join([str(item) for item in new_top_users_name]),
            top_users_tag = ' '.join([str(item) for item in new_top_users_tag]),
            points = ' '.join([str(item) for item in new_points]),
            size = size
        )

        # Commit new local leaderboard to DB
        session.add(new_localboard)
        session.commit()

        return new_localboard

    @staticmethod
    def update_local_leaderboard(member:Member, session:Session):
        leaderboard = LocalLeaderboard.get_local_leaderboard(member, session)
        size = leaderboard.size
        top_users_id = leaderboard.top_users_id.split(' ')
        top_users_name = leaderboard.top_users_name.split(' ')
        top_users_tag = leaderboard.top_users_tag.split(' ')
        points = leaderboard.points.split(' ')

        current_user = EconomyAccount.get_economy_account(member, session)
        
        LocalLeaderboard.remove_from_board(
            member,
            session,
        )

        rank = LocalLeaderboard.add_to_board(
            member,
            session,
            current_user,
        )
        
        return rank
    
    @staticmethod
    def add_to_board(member:Member, session:Session, current_user):
        leaderboard = LocalLeaderboard.get_local_leaderboard(member, session)
        user_id = str(member.id)

        size = leaderboard.size
        top_users_id = leaderboard.top_users_id.split(' ')
        top_users_name = leaderboard.top_users_name.split(' ')
        top_users_tag = leaderboard.top_users_tag.split(' ')
        points = leaderboard.points.split(' ')

        for rank in range(size):
            if (current_user.balance > int(points[rank])) or (top_users_name[rank] == '---'):
                # Replace the last place
                if rank == size-1:
                    top_users_id[rank] = str(member.id)
                    top_users_name[rank] = str(member.name)
                    top_users_tag[rank] = str(member.discriminator)
                    points[rank] = str(current_user.balance)

                    leaderboard.top_users_id = ' '.join([str(item) for item in top_users_id]) 
                    leaderboard.top_users_name = ' '.join([str(item) for item in top_users_name]) 
                    leaderboard.top_users_tag = ' '.join([str(item) for item in top_users_tag])
                    leaderboard.points = ' '.join([str(item) for item in points]) 
                    session.commit()
                    return rank+1
                # Replace the <rank>th place
                else:
                    pos = size-1
                    while pos != rank:
                        top_users_id[pos] = top_users_id[pos-1]
                        top_users_name[pos] = top_users_name[pos-1]
                        top_users_tag[pos] = top_users_tag[pos-1]
                        points[pos] = points[pos-1]
                        pos -= 1
                    
                    top_users_id[rank] = str(member.id)
                    top_users_name[rank] = str(member.name)
                    top_users_tag[rank] = str(member.discriminator)
                    points[rank] = str(current_user.balance)
                    
                    leaderboard.top_users_id = ' '.join([str(item) for item in top_users_id])
                    leaderboard.top_users_name = ' '.join([str(item) for item in top_users_name]) 
                    leaderboard.top_users_tag = ' '.join([str(item) for item in top_users_tag])
                    leaderboard.points = ' '.join([str(item) for item in points]) 
                    session.commit()
                    return rank+1

        return 0

    @staticmethod
    def remove_from_board(member:Member, session:Session):
        leaderboard = LocalLeaderboard.get_local_leaderboard(member, session)
        user_id = str(member.id)

        size = leaderboard.size
        top_users_id = leaderboard.top_users_id.split(' ')
        top_users_name = leaderboard.top_users_name.split(' ')
        top_users_tag = leaderboard.top_users_tag.split(' ')
        points = leaderboard.points.split(' ')

        if user_id in top_users_id:
            index = top_users_id.index(user_id)
            for pos in range(index, size-2):
                top_users_id[pos] = top_users_id[pos+1]
                top_users_name[pos] = top_users_name[pos+1]
                top_users_tag[pos] = top_users_tag[pos+1]
                points[pos] = points[pos+1]

            top_users_id[size-1] = '0'
            top_users_name[size-1] = '---'
            top_users_tag[size-1] = '0'
            points[size-1] = '0'

            leaderboard.top_users_id = ' '.join([str(item) for item in top_users_id]) 
            leaderboard.top_users_name = ' '.join([str(item) for item in top_users_name]) 
            leaderboard.top_users_tag = ' '.join([str(item) for item in top_users_tag])
            leaderboard.points = ' '.join([str(item) for item in points]) 
            session.commit()