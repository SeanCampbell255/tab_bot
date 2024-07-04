import pandas as pd
import common.env as env 
import common.utils as utils  
import os
import sqlite3
from datetime import datetime as dt

from src.services.ddl import TABLE_DDL

class DBConnector():
    def __init__(self) -> None:
        self.db_location = env.get_db_location()
        self.con = sqlite3.connect(self.db_location, autocommit=True)
        self.cur = self.con.cursor()
        self._create_tables_if_not_exist(TABLE_DDL)

    def _create_tables_if_not_exist(self, tables):
        for ddl in tables:
            self.cur.execute(ddl)
    
    def get_user_payment_status_by_tab(self, event: dict):
        tab_id = event.get("tab_id")
        user_id = event.get("user_id")
        try:
            self.cur.execute(
                f"""
                SELECT name,
                user_id, 
                tab_id, 
                recipient_user_id,
                amount_owed, 
                amount_remaining, 
                paid, 
                over_paid 
                FROM USER_PAYMENT_STATUS 
                WHERE User_id = {user_id} and Tab_Id = {tab_id}
                """
            )

            _res = self.cur.fetchall()[0]
        except Exception as e:
            print(e)
            return {}

        return {
                "name": _res[0],
                "user_id": _res[1],
                "tab_id": _res[2],
                "recipient_user_id": _res[3],
                "amount_owed": _res[4],
                "amount_remaining": _res[5],
                "paid": bool(_res[6]),
                "over_paid": bool(_res[7]),
            }

    def get_user_payment_status(self, user_id: int):
        OVERPAYMENT_QUERY = """
            SELECT 
                user_id, 
                tab_id, 
                recipient_user_id,
                amount_owed, 
                amount_remaining, 
                paid, 
                over_paid,
                created_date
                FROM USER_PAYMENT_STATUS 
                WHERE user_id = {user_id}
                AND paid = 0
                ORDER BY created_date asc
        """
        self.cur.execute(OVERPAYMENT_QUERY.format(user_id=user_id))
        return [
            {
                "user_id": tab[0],
                "tab_id": tab[1],
                "recipient_user_id": tab[2],
                "amount_owed": tab[3],
                "amount_remaining": tab[4],
                "paid": tab[5],
                "over_paid": tab[6],
                "created_date": tab[7]
            }
            for tab in self.cur.fetchall()
            ]
    
    
    def create_payment(self, event: dict):
        tab_id = event.get("tab_id")
        user_id = event.get("user_id")
        amount = event.get("amount")

        try:
            self.cur.execute(
                f"""
                INSERT INTO USER_PAYMENTS_MAP(
                    user_id,
                    tab_id,
                    amount,
                    payment_date
                    )
                VALUES(
                {user_id}, {tab_id}, {amount}, datetime('now','localtime')
                )
                """
            )
            print("Payment Successful!")
        except Exception as e:
            print(str(e))
            raise 

    def update_user_tab_map(self, payment_status: dict):
        if payment_status.get("paid"):
            user_id = payment_status.get("user_id")
            tab_id = payment_status.get("tab_id")
            try:
                self.cur.execute(
                    f"""
                    UPDATE USER_TAB_MAP
                    SET paid = 1
                    WHERE user_id = {user_id} AND tab_id = {tab_id}
                    """
                )
                print(f"Tab {tab_id} has been paid by {payment_status.get("name")}!")
            except Exception as e:
                print(str(e))
                raise 

    def handle_remaining_overpayment(self, payment_status: dict):
        amount_remaining = abs(float(payment_status.get("amount_remaining")))
        sender_id = payment_status.get("recipient_user_id")
        recipient_id = payment_status.get("user_id")
        
        try:
            # Create a new tab to handle overpayments
            self.cur.execute(
            f"""
            INSERT INTO TABS(
                name,
                total_amount,
                description,
                emoji,
                created_date 
                )
            VALUES(
            "OVERPAYMENT", {amount_remaining},"OVERPAYMENT FOR TAB {payment_status.get("tab_id")}", "", datetime('now','localtime')
            )
            RETURNING tab_id; 
            """
            )
            tab_id = self.cur.fetchone()[0]
            print(f"New Tab Created for Overpayment for the amount of {amount_remaining} with tab id {tab_id}")
        except Exception as e:
            print(str(e))
            raise

        if tab_id:
            # Create User Tab Mappings
            try:
                self.cur.execute(
                    f"""
                    INSERT INTO USER_TAB_MAP(
                        user_id,
                        tab_id,
                        amount_owed,
                        recipient
                        )
                    VALUES
                    ({sender_id}, {tab_id}, {amount_remaining}, 0),
                    ({recipient_id}, {tab_id}, 0, 1)
                    """
                )
            except Exception as e:
                print(str(e))
                raise 
    
    def clear_users(self):
        query = """
        DELETE FROM USERS;
        """
        try:
            self.cur.execute(query)
            print(f"Users Cleared!")
        except Exception as e:
            print(str(e))
            raise
        
    def insert_users(self, users):
        values = []
        fstring ="""
                (
                {user_id}, {name},{insert_date}
                )
                """
        for user in users:
            _val = fstring.format(user_id=user.get("user_id"), name=user.get("name"), insert_date=user.get("insert_date"))
            values.append(_val)
        
        values_str = " ,".join(values)

        query = f"""
        INSERT INTO USERS(
            user_id, 
            name, 
            insert_date
                )
        VALUES
        {values_str}
        """
        try:
            self.cur.execute(query)
            print(f"Users Inserted!")
        except Exception as e:
            print(str(e))
            raise



    def get_payments_by_user(self, user_id):
        pass

    def log_to_db(self, table_name, event):
        pass