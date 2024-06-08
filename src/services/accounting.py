# Big SEAN
import pandas as pd
from decimal import Decimal
class Accounting:
    """
    Class representing mathematical operations
    Intake and adjustment of balances and tabs
    Business Rules

    Add, subtract, Percentage
    Calculate Balances(?)
    Calculate Amount Due (?)
    """
    pass

    def get_total_balance(self, name):
        """
        Returns the total balance name owes
        """

    def get_balance(self, name, id):
        """
        Returns the balance name owes on 'id'
        """

    def get_user_balances(self, name):
        """
        Returns summary of balances owed/debted for 'name'
        """

    def get_balance_details(self, id):
        """
        Returns details of balance 'id'
        """

    def pay_balance(self, name, id):
        """
        Sets the balance name owes on 'id' to zero
        -also log into resultant db
        """

    def pay_partial_balance(self, name, id, amount_paid):
        """
        Sets the balance name owes on 'id' to (balance - amount_paid)
        -also log into resultant db
        """

    def set_balance_unpaid(self, name, id):
        """
        Resets the balance name owes on 'id' to its original balance
        -also log into resultant db
        """
