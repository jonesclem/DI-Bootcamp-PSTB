#### EXERCISE XP - WEEK 1 - DAY 4

### Exercise 1: Pets

"""Use the provided Pets and Cat classes to create a Siamese breed, instantiate cat objects, 
and use the Pets class to manage them."""

class Pets():
    def __init__(self, animals):
        self.animals = animals

    def walk(self):
        for animal in self.animals:
            print(animal.walk())

class Cat():
    is_lazy = True

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def walk(self):
        return f'{self.name} is just walking around'

class Bengal(Cat):
    def sing(self, sounds):
        return f'{sounds}'

class Chartreux(Cat):
    def sing(self, sounds):
        return f'{sounds}'

# Step 1: Create the Siamese Class
# Create a class called Siamese that inherits from the Cat class.
# You can add any specific attributes or methods for the Siamese breed,
# or leave it as is if there are no unique behaviors.

class Siamese(Cat):
    def sing(self, sounds):
        return f'{sounds}'

# Step 2: Create a List of Cat Instances

# Create a list called all_cats that contains instances of Bengal, Chartreux, and Siamese cats.
# Example: all_cats = [bengal_obj, chartreux_obj, siamese_obj]
# Give each cat a name and age.

bengal_obj = Bengal("BengalCat", 3)
chartreux_obj = Chartreux("ChartreuxCat", 4)
siamese_obj = Siamese("SiameseCat", 2)
all_cats = [bengal_obj, chartreux_obj, siamese_obj]

#print(all_cats)

# Step 3: Create a Pets Instance
"""Creating an instance of the Pets class called sara_pets, passing the all_cats list as an argument"""
sara_pets = Pets(all_cats)
print("sara_pets instance created")

# Step 4: Take Cats for a Walk
# Call the walk() method on the sara_pets instance.
# This should print the result of calling the walk() method on each cat in the list.
print(sara_pets.walk())


## Exercise 2: Dogs
# Goal: Create a Dog class with methods for barking, running speed, and fighting.

# Step 1: Create the Dog Class

# Create a class called Dog with name, age, and weight attributes.
# Implement a bark() method that returns “ is barking”.
# Implement a run_speed() method that returns weight / age * 10.
# Implement a fight(other_dog) method that returns a string indicating which dog won the fight, based on run_speed * weight.

class Dog():
    def __init__(self, name, age, weight):
        self.name = name
        self.age = age
        self.weight = weight

    def bark(self):
        return f"{self.name} is barking"

    def run_speed(self):
        return f"{self.name} run speed is {(self.weight / self.age) * 10}"
    
    """ Implement a fight(other_dog) method that returns a string indicating which dog won the fight, 
    based on run_speed * weight."""

    def fight(self, other_dog):
        if (self.run_speed() * self.weight) > (other_dog.run_speed() * other_dog.weight):
            return f"The winner is {self.name}"
        else:
            return f"The winner is {other_dog.name}"
        

# Step 2: Create Dog Instances
# Create three instances of the Dog class with different names, ages, and weights.

dog1 = Dog("Idefix", 3, 10)
dog2 = Dog("Titou", 4, 15)
dog3 = Dog("Moloss", 5, 20)

# Step 3: Test Dog Methods
# Call the bark(), run_speed(), and fight() methods on the dog instances to test their functionality.

print(dog1.bark())
print(dog2.bark())
print(dog3.bark())
print(dog1.run_speed())
print(dog2.run_speed())
print(dog3.run_speed())
print(dog1.fight(dog2))
print(dog1.fight(dog3))




