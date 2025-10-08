## Exercise 4: Family and Person Classes
# Goal:
# Practice working with classes and object interactions by modeling a family and its members.

# Instructions:

# Step 1: Create the Person Class

# Define a Person class with the following attributes:
# first_name
# age
# last_name (string, should be initialized as an empty string)
# Add a method called is_18():
# It should return True if the person is 18 or older, otherwise False.

class Person():
    def __init__(self, first_name, age, last_name=""):
        self.first_name = first_name
        self.age = age
        self.last_name = last_name
    
    def is_18(self):
        if self.age >= 18:
            return True
        else:
            return False
        
# Step 2: Create the Family Class

# Define a Family class with:
# A last_name attribute
# A members list that will store Person objects (should be initialized as an empty list)

class Family():
    def __init__(self, last_name):
        self.last_name = last_name
        self.members = [] #defining the members list initialized as empty list

# Add a method called born(first_name, age):
#  It should create a new Person object with the given first name and age.
#  It should assign the family’s last name to the person.
#  It should add this new person to the members list.

    def born(self, first_name, age):
        new_member = Person(first_name, age)
        new_member.last_name = self.last_name
        self.members.append(new_member)
    
# Add a method called check_majority(first_name):

#   It should search the members list for a person with that first_name.
#   If the person exists, call their is_18() method.
#   If the person is over 18, print:
#   "You are over 18, your parents Jane and John accept that you will go out with your friends"
#   Otherwise, print:
#   "Sorry, you are not allowed to go out with your friends."

    def check_majority(self, first_name):
        for member in self.members:
            if first_name == member.first_name:
                is18 = member.is_18()
                if is18:
                    print(f"{member.first_name}, you are over 18, your parents Jane and John accept that you will go out with your friends")
                else:
                    print(f"Sorry {member.first_name}, you are not allowed to go out with your friends.")
        #print(f"No member found with the name {first_name}")
    
# Add a method called family_presentation():

# It should print the family’s last name.
#  Then, it should print each family member’s first name and age.

    def family_presentation(self):
        print(f"Presenting the {self.last_name} family: ")
        for member in self.members:
            print(f"{member.first_name} is {member.age} years old")


"""Creating a family instance and testing the program"""

print("Creating the Lovely family")
lovely_family = Family("Lovely")
lovely_family.born("John", 45)
lovely_family.born("Jane", 43)
lovely_family.born("Ben", 30)
lovely_family.born("Elsa", 16)
lovely_family.check_majority("Ben")
lovely_family.check_majority("Elsa")
lovely_family.family_presentation()
#lovely_family.check_majority("Charlie")  # Testing a non-existing family member