# #### RETOUR SUR LES NOTIONS DE DAY 2, MAP, REDUCE, LAMBDA

# def upper_string(s):
#     return s.upper()

# fruit = ["Apple", "Banana", "Pear", "Apricot", "Orange"]
# map_object = map(upper_string, fruit)

# print(list(map_object)) # le return de map object c'est un objet en mémoire. on doit force l'affichage en list



# def starts_with_A(s):
#     return s[0] == "A"

# fruit = ["Apple", "Banana", "Pear", "Apricot", "Orange"]
# filtered_object = filter(starts_with_A, fruit)

# print(list(filtered_object))
# #['Apple', 'Apricot']


# from functools import reduce # appeler la function reduce

# def sum_numbers(first, second):
#     return first+second

# my_list = [1, 3, 5, 7]
# reduced_list = reduce(sum_numbers, my_list) # ca fait 1+3, puis resultat + 5, puis resultat + 7

# print(reduced_list)
# # >> 16


# fruit = ["Apple", "Banana", "Pear", "Apricot", "Orange"]
# map_object = map(lambda s: s.upper(), fruit) # fait le job direct en une ligne, lambda cree la fonction et return direct la value sans declarer

# print(list(map_object))

# fruit = ["Apple", "Banana", "Pear", "Apricot", "Orange"]
# filtered_object = filter(lambda s: s[0] == "A", fruit)

# print(list(filtered_object))


# from functools import reduce
# my_list = [1, 3, 5, 7]
# reduced_list = reduce(lambda first, second: first+second, my_list)
# print(reduced_list)


# ## challenge
# people = ["Rick", "Morty", "Beth", "Jerry", "Snowball"]

# #Using map and filter, try to say hello to everyone who's name is less than or equal to 4 letters

# short = filter(lambda s: len(s) <= 4, people)
# #Etape 2 = dire bonjour à chacun
# salutations = map(lambda s: f"Hello {s}!", short)
# #Etape 3 = afficher le résultat
# for cc in salutations:
#     print(cc)



# ##### NOTIONS DU DAY 3


# class Dog():
#     pass

# shelter_dog = Dog() # Here we created shelter_dog, an object of the class Dog.


# #To define a new attribute (or modify an existing one), target it and assign it to his new value with the equal sign =.

# class Dog():
#     pass

# shelter_dog = Dog()
# shelter_dog.color = "Brown"


# class Dog():
#     # Initializer / Instance Attributes
#     def __init__(self, name_of_the_dog): # init obligatoire pour la def de class + le param self pour dire python on fait de l'objet
#         print("A new dog has been initialized !")
#         print("His name is", name_of_the_dog)

# shelter_dog = Dog(name_of_the_dog="Rex")
# # or
# shelter_dog = Dog("Rex")

# # en fait python fait: shelter_dog = Dog(shelter_dog, "Rex")


# class Person():
#   def __init__(self, name, age): #init
#     self.name = name # def attribute
#     self.age = age # def attribute

# first_person = Person("John", 36) # creer la premiere valeur

# print(first_person.name) # chercher nom first person
# print(first_person.age) # chercher age first person


# #### INSTANCE METHODS

# # a partir de l'image robot et person on peut creer les deux class et les 4 instances avec creation attributs

# class Dog():
#     # Initializer / Instance Attributes
#     def __init__(self, name_of_the_dog):
#         print("A new dog has been initialized !")
#         print("His name is", name_of_the_dog)
#         self.name = name_of_the_dog

#     def bark(self):
#         print(f"{self.name} barks ! WAF")

#     def walk(self, number_of_meters):
#         print(f"{self.name} walked {number_of_meters} meters")

# shelter_dog = Dog("Rex")
# shelter_dog.bark()
# shelter_dog.walk(10)


# # autre exo rename name

# class Person():
#   def __init__(self, name, age):
#     self.name = name
#     self.age = age

#   def show_details(self):
#     print("Hello my name is " + self.name)
    
#   def rename(self, new_name):
#      self.name = new_name

# first_person = Person("John", 36)
# first_person.show_details()
# first_person.rename("Paul")
# first_person.show_details()

## class BankAccount: et class BankAccount(): >>> les deux marchent

## code example, class and object

class BankAccount:

    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance
        self.transactions = []

    def view_balance(self):
        self.transactions.append("View Balance")
        print(f"Balance for account {self.account_number}: {self.balance}")

    def deposit(self, amount):
        if amount <= 0:
            print("Invalid amount")
        elif amount < 100:
            print("Minimum deposit is 100")
        else:
            self.balance += amount
            self.transactions.append(f"Deposit: {amount}")
            print("Deposit Succcessful")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient Funds")
        else:
            self.balance -= amount
            self.transactions.append(f"Withdraw: {amount}")
            print("Withdraw Approved")
            return amount

    def view_transactions(self):
        print("Transactions:")
        print("-------------")
        for transaction in self.transactions:
            print(transaction)

compte1 = BankAccount(23343434,0)



