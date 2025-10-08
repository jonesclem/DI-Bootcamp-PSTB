class BankAccount:
    def __init__(self, username: str = "", password: str = "", balance: int = 0):
        if balance < 0:
            raise ValueError("Le solde initial ne peut pas être négatif.")
        self.balance = balance
        self.username = username
        self.password = password
        self.authenticated = False

    def authenticate(self, username: str, password: str) -> bool:
        """
        Met authenticated=True si les identifiants correspondent.
        Retourne True si succès, False sinon.
        """
        self.authenticated = (self.username == username and self.password == password)
        return self.authenticated

    def _ensure_auth(self):
        if not self.authenticated:
            raise PermissionError("Action refusée : utilisateur non authentifié.")

    def deposit(self, amount: int):
        self._ensure_auth()
        if not isinstance(amount, int):
            raise TypeError("Le montant doit être un entier (int).")
        if amount <= 0:
            raise ValueError("Montant de dépôt doit être strictement positif.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: int):
        self._ensure_auth()
        if not isinstance(amount, int):
            raise TypeError("Le montant doit être un entier (int).")
        if amount <= 0:
            raise ValueError("Montant de retrait doit être strictement positif.")
        if amount > self.balance:
            raise ValueError("Fonds insuffisants.")
        self.balance -= amount
        return self.balance


class MinimumBalanceAccount(BankAccount):
    def __init__(self, username: str = "", password: str = "", balance: int = 0, minimum_balance: int = 0):
        super().__init__(username=username, password=password, balance=balance)
        if minimum_balance < 0:
            raise ValueError("Le minimum autorisé ne peut pas être négatif.")
        self.minimum_balance = minimum_balance

    def withdraw(self, amount: int):
        # Auth + validations de base via la classe mère, mais on contrôle avant le solde minimum :
        self._ensure_auth()
        if not isinstance(amount, int):
            raise TypeError("Le montant doit être un entier (int).")
        if amount <= 0:
            raise ValueError("Montant de retrait doit être strictement positif.")
        if self.balance - amount < self.minimum_balance:
            raise ValueError("Retrait refusé : minimum de solde dépassé.")
        # Puis on applique la logique commune (décrément + garde-fous)
        return super().withdraw(amount)


class ATM:
    def __init__(self, account_list: list, try_limit: int = 2):
        # Valider la liste de comptes
        if not isinstance(account_list, list) or not all(isinstance(acc, BankAccount) for acc in account_list):
            raise TypeError("account_list doit être une liste d'instances BankAccount (ou MinimumBalanceAccount).")
        self.account_list = account_list

        # Gérer try_limit selon le brief : si invalide → on signale puis on met 2
        if not isinstance(try_limit, int) or try_limit <= 0:
            print("Avertissement: try_limit invalide. Valeur par défaut 2 appliquée.")
            try_limit = 2
        self.try_limit = try_limit
        self.current_tries = 0

    def show_main_menu(self):
        while True:
            print("\n=== ATM ===")
            print("1. Log in")
            print("2. Exit")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self._handle_login_flow()
            elif choice == "2":
                print("Exiting...")
                break
            else:
                print("Option invalide, réessayez.")

    def _handle_login_flow(self):
        self.current_tries = 0
        while self.current_tries < self.try_limit:
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            account = self._authenticate_any(username, password)
            if account:
                print("Login successful!")
                self.show_account_menu(account)
                return
            self.current_tries += 1
            print(f"Login failed. Attempt {self.current_tries} of {self.try_limit}.")
        print("Maximum login attempts reached. Shutting down.")
        # On sort proprement de l'appli
        raise SystemExit(0)

    def _authenticate_any(self, username: str, password: str):
        for account in self.account_list:
            if account.authenticate(username, password):
                return account
        return None

    def show_account_menu(self, account: BankAccount):
        while True:
            print("\n=== Account Menu ===")
            print("1. Deposit")
            print("2. Withdraw")
            print("3. Balance")
            print("4. Logout")
            choice = input("Select an option: ").strip()
            if choice == "1":
                try:
                    amount = int(input("Enter amount to deposit: "))
                    new_balance = account.deposit(amount)
                    print(f"Deposited {amount}. New balance is {new_balance}.")
                except Exception as e:
                    print(f"Erreur: {e}")
            elif choice == "2":
                try:
                    amount = int(input("Enter amount to withdraw: "))
                    new_balance = account.withdraw(amount)
                    print(f"Withdrew {amount}. New balance is {new_balance}.")
                except Exception as e:
                    print(f"Erreur: {e}")
            elif choice == "3":
                print(f"Current balance: {account.balance}")
            elif choice == "4":
                # On “déconnecte” simplement le flag
                account.authenticated = False
                print("Logged out.")
                break
            else:
                print("Option invalide, réessayez.")


if __name__ == "__main__":
    print("Creating accounts...")
    acc1 = BankAccount("user1", "pass1", balance=0)
    acc2 = MinimumBalanceAccount("user2", "pass2", balance=300, minimum_balance=100)
    atm = ATM([acc1, acc2], try_limit=3)
    atm.show_main_menu()