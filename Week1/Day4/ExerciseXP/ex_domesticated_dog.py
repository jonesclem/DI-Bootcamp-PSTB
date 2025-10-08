#### EXERCISE XP - WEEK 1 - DAY 4

## Exercise 3: Dogs Domesticated
# Goal: Create a PetDog class that inherits from Dog and adds training and tricks.

# Instructions:
# Step 1: Import the Dog Class
#  In a new Python file, import the Dog class from the previous exercise.

from ex_pets_dogs import Dog
import random

# Step 2: Create the PetDog Class

#  Create a class called PetDog that inherits from the Dog class.
#  Add a trained attribute to the __init__ method, with a default value of False.
#  trained means that the dog is trained to do some tricks.
#  Implement a train() method that prints the output of bark() and sets trained to True.
#  Implement a play(*args) method that prints “ all play together”.
#  *args on this method is a list of dog instances.
#  Implement a do_a_trick() method that prints a random trick if trained is True.
#  Use this list for the ramdom tricks:
#  tricks = ["does a barrel roll", "stands on his back legs", "shakes your hand", "plays dead"]
#  Choose a rendom index from it each time the method is called.

class PetDog(Dog):
    def __init__(self, name, age, weight, trained=False):
        self.name = name
        self.age = age
        self.weight = weight
        self.trained = trained
    
    def train(self): 
        print(self.bark())
        self.trained = True

    def play(self, *args):
        dog_names = ", ".join([dog for dog in args])
        print(f"{self.name}, {dog_names} all play together")
    
    def do_a_trick(self):
        tricks = ["does a barrel roll", "stands on his back legs", "shakes your hand", "plays dead"]
        if self.trained is True:
            print(f"{self.name} {random.choice(tricks)}")
    
#Step 3: Test PetDog Methods
#Create instances of the PetDog class and test the train(), play(*args), and do_a_trick() methods.
my_dog = PetDog("Fido", 2, 10)
my_dog.train()
my_dog.play("Buddy", "Max")
my_dog.do_a_trick()