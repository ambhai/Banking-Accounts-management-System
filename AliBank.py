import random
import csv
import json
import os
import hashlib
from datetime import datetime

ACCOUNTS_FILE = "accounts.json"
TRANSACTIONS_FILE = "transactions.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Bank:
    def __init__(self, username, address, cnic, password, account_number=None, balance=0.0, transactions=None):
        self.username = username
        self.address = address
        self.cnic = cnic
        self.password = password
        self.account_number = account_number or f"ACC{random.randint(100000, 999999)}"
        self.balance = balance
        self.transactions = transactions or []

        self._create_transaction_file()

    def _create_transaction_file(self):
        if not os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Account Number", "Username", "Type", "Amount", "Balance", "Timestamp"])

    def _log_transaction(self, t_type, amount):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append((t_type, amount, self.balance, timestamp))

        with open(TRANSACTIONS_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.account_number, self.username, t_type, amount, self.balance, timestamp])

    def deposit(self, amount):
        self.balance += amount
        print(f"\n✅ {amount} deposited successfully.")
        print(f"📊 New Balance: {self.balance:.2f}")
        self._log_transaction("Deposit", amount)

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            print(f"\n✅ {amount} withdrawn successfully.")
            print(f"📉 New Balance: {self.balance:.2f}")
            self._log_transaction("Withdraw", amount)
        else:
            print("\n❌ Insufficient balance.")

    def mini_statement(self):
        print(f"\n🧾 Mini Statement for {self.username} (Account: {self.account_number}):")
        for t_type, amount, balance, timestamp in self.transactions:
            print(f"{timestamp} | {t_type} | Amount: {amount} | Balance: {balance:.2f}")
        print()

    def to_dict(self):
        return {
            "username": self.username,
            "address": self.address,
            "cnic": self.cnic,
            "password": self.password,
            "account_number": self.account_number,
            "balance": self.balance,
            "transactions": self.transactions
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data["username"],
            address=data["address"],
            cnic=data["cnic"],
            password=data.get("password", ""),
            account_number=data["account_number"],
            balance=data["balance"],
            transactions=data.get("transactions", [])
        )

class BankSystem:
    def __init__(self):
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r') as file:
                data = json.load(file)
                return {acc_num: Bank.from_dict(acc_data) for acc_num, acc_data in data.items()}
        return {}

    def _save_accounts(self):
        with open(ACCOUNTS_FILE, 'w') as file:
            json.dump({acc_num: acc.to_dict() for acc_num, acc in self.accounts.items()}, file, indent=4)

    def create_account(self):
        print("\n--- Create New Account ---")
        username = input("Enter your name: ")
        address = input("Enter your address: ")

        # CNIC validation: must be 13-digit numeric
        while True:
            cnic = input("Enter your 13-digit CNIC (numbers only): ")
            if cnic.isdigit() and len(cnic) == 13:
                cnic = int(cnic)
                break
            else:
                print("❌ CNIC must be exactly 13 digits and numeric.")

        # Password validation: must be 4-digit numeric
        while True:
            password = input("Set a 4-digit numeric password: ")
            confirm = input("Confirm password: ")
            if not (password.isdigit() and len(password) == 4):
                print("❌ Password must be exactly 4 digits and numeric.")
            elif password != confirm:
                print("❌ Passwords do not match. Try again.")
            else:
                break

        hashed_pw = hash_password(password)
        new_account = Bank(username, address, cnic, hashed_pw)
        self.accounts[new_account.account_number] = new_account
        self._save_accounts()

        print(f"\n🎉 Account created! Your account number is {new_account.account_number}")
        return new_account

    def login(self):
        print("\n--- Login to Your Account ---")
        account_number = input("Enter your account number: ")
        if account_number in self.accounts:
            password = input("Enter your password: ")
            hashed_input = hash_password(password)
            account = self.accounts[account_number]
            if account.password == hashed_input:
                print(f"\n🔓 Welcome back, {account.username}!")
                return account
            else:
                print("❌ Incorrect password.")
        else:
            print("❌ Account not found.")
        return None

    def main_menu(self):
        while True:
            print("\n====== BANK SYSTEM MENU ======")
            print("1. Create New Account")
            print("2. Login to Existing Account")
            print("3. Exit")

            choice = input("Choose an option: ")

            if choice == '1':
                account = self.create_account()
                self.account_menu(account)
            elif choice == '2':
                account = self.login()
                if account:
                    self.account_menu(account)
            elif choice == '3':
                print("\n👋 Thank you for using Allied Bank. Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")

    def account_menu(self, account):
        while True:
            print("\n--- Account Menu ---")
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Mini Statement")
            print("4. Logout")

            choice = input("Select option: ")

            if choice == '1':
                try:
                    amount = float(input("Enter amount to deposit: "))
                    account.deposit(amount)
                    self._save_accounts()
                except ValueError:
                    print("❌ Invalid amount.")
            elif choice == '2':
                try:
                    amount = float(input("Enter amount to withdraw: "))
                    account.withdraw(amount)
                    self._save_accounts()
                except ValueError:
                    print("❌ Invalid amount.")
            elif choice == '3':
                account.mini_statement()
            elif choice == '4':
                print(f"\n🔒 Logged out of account {account.account_number}.")
                break
            else:
                print("❌ Invalid option.")

# Run the full bank system
if __name__ == "__main__":
    system = BankSystem()
    system.main_menu()
