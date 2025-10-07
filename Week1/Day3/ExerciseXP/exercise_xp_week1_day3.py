## Exercises XP - Week 1 - Day


# Instructions:
# Use the provided Cat class to create three cat objects. Then, create a function to find the oldest cat and print its details.

class Cat:
    def __init__(self, cat_name, cat_age):
        self.name = cat_name
        self.age = cat_age
# Step 1: Create Cat Objects
# Use the Cat class to create three cat objects with different names and ages.

cat1 = Cat("Bib", 10)
cat2 = Cat("Bab", 12)
cat3 = Cat("Bob", 15)

# Step 2: Create a Function to Find the Oldest Cat

#     Create a function that takes the three cat objects as input.
#     Inside the function, compare the ages of the cats to find the oldest one.
#     Return the oldest cat object.

def find_oldest_cat(cat1, cat2, cat3):
    if cat1.age >= cat2.age and cat1.age >= cat3.age:
        return cat1
    elif cat2.age >= cat1.age and cat2.age >= cat3.age:
        return cat2
    else:
        return cat3
# Step 3: Print the Oldest Cat’s Details

#     Call the function to get the oldest cat.
#     Print a formatted string: “The oldest cat is <cat_name>, and is <cat_age> years old.”
#     Replace <cat_name> and <cat_age> with the oldest cat’s name and age.
oldest_cat = find_oldest_cat(cat1, cat2, cat3)
print(f"The oldest cat is {oldest_cat.name}, and is {oldest_cat.age} years old.")


# Exercise 2 : Dogs

# Goal: Create a Dog class, instantiate objects, call methods, and compare dog sizes.

#Instructions:
#Create a Dog class with methods for barking and jumping. Instantiate dog objects, call their methods, and compare their sizes.

# Step 1: Create the Dog Class

#     Create a class called Dog.
#     In the __init__ method, take name and height as parameters and create corresponding attributes.
#     Create a bark() method that prints “ goes woof!”.
#     Create a jump() method that prints “ jumps cm high!”, where x is height * 2.
class Dog():
    # Initializer / Instance Attributes
    def __init__(self, name, height):
        self.name = name
        self.height = height
    
    def bark(self):
        print(f"{self.name} goes woof!")

    def jump(self):
        #jump_height = self.height * 2 # other method to calculate the jump height
        #print(f"{self.name} jumps {jump_height} cm high!") # other method to print the jump height
        print(f"{self.name} jumps {self.height * 2} cm high")

# Step 2: Create Dog Objects
#  Create davids_dog and sarahs_dog objects with their respective names and heights.
davids_dog = Dog("Chew", 30)
sarahs_dog = Dog("Backa", 50)
# Step 3: Print Dog Details and Call Methods

#  Print the name and height of each dog.
print(f"{davids_dog.name} is {davids_dog.height} cm tall.")
print(f"{sarahs_dog.name} is {sarahs_dog.height} cm tall.")
#  Call the bark() and jump() methods for each dog.
davids_dog.bark()
davids_dog.jump()

sarahs_dog.bark()
sarahs_dog.jump()

# Step 4: Compare Dog Sizes
if davids_dog.height > sarahs_dog.height:
    print(f"The bigger dog is {davids_dog.name}.")
elif sarahs_dog.height > davids_dog.height:
    print(f"The bigger dog is {sarahs_dog.name}.")
else:
    print("Both dogs are the same height!")

#Exercise 3 : Who’s the song producer?

#Goal: Create a Song class to represent song lyrics and print them.

#Instructions:
#Create a Song class with a method to print song lyrics line by line.
# Step 1: Create the Song Class
#     Create a class called Song.
#     In the __init__ method, take lyrics (a list) as a parameter and create a corresponding attribute.
#     Create a sing_me_a_song() method that prints each element of the lyrics list on a new line.
class Song():
# Initializer / Instance Attributes
    def __init__(self, lyrics):
        self.lyrics = lyrics
    
    def sing_me_a_song(self):
        for line in self.lyrics:
            print(line)

#Example:
stairway = Song(["There’s a lady who's sure", "all that glitters is gold", "and she’s buying a stairway to heaven"])
                
# Displaying the lyrics of the song with each element on a new line
stairway.sing_me_a_song()


#Exercise 4 : Afternoon at the Zoo

#Goal:
#Create a Zoo class to manage animals. The class should allow adding animals, displaying them, selling them, and organizing them into alphabetical groups.

# Instructions
# Step 1: Define the Zoo Class

# 1. Create a class called Zoo.

class Zoo():
    
# 2. Implement the __init__() method:
#     It takes a string parameter zoo_name, representing the name of the zoo.
#     Initialize an empty list called animals to keep track of animal names.
    def __init__(self, zoo_name):
        self.name = zoo_name
        self.animals = []

# 3. Add a method add_animal(new_animal):

#     This method adds a new animal to the animals list.
#     Do not add the animal if it is already in the list.
    def add_animal(self, new_animal):
        if new_animal not in self.animals:
            self.animals.append(new_animal)

# 4. Add a method get_animals():
#     This method prints all animals currently in the zoo.

    def get_animals(self):
        print("This is all the animals in the zoo:", end = "" )
        for i in self.animals:
            print (f" {i}", end= "")

# 5. Add a method sell_animal(animal_sold):
#     This method checks if a specified animal exists on the animals list and if so, remove from it.

    def sell_animal(self, animal_sold):
        if animal_sold in self.animals:
            self.animals.remove(animal_sold)
            print(f"\n{animal_sold} has been sold.")
        else:
            print(f"\n{animal_sold} is not in the zoo.")

# 6. Add a method sort_animals():

#     This method sorts the animals alphabetically.
#     It also groups them by the first letter of their name.
#     The result should be a dictionary where:
#         Each key is a letter.
#         Each value is a list of animals that start with that letter.
    def sort_animals(self):
        self.animals.sort() # sorting the animals alphabetically.
        grouped_animals = {} # creating an empty dictionary
        for animal in self.animals: #iterating through each animal of the list
            first_letter = animal[0] # We take the first letter of each animal name
            if first_letter not in grouped_animals:
                grouped_animals[first_letter] = [] # create an empty list to receive the values
            grouped_animals[first_letter].append(animal) # add the first letter to the list to build the final object
        self.grouped_animals = grouped_animals
        #print(grouped_animals) >>> display the dictionary without formatting
        # Organising the dictionary formatting inside the print
        print("\n\n{")
        for i,v in grouped_animals.items():
            print(f"  {i}: {v}")
        print("}\n")

# Example output:
# {
#    'B': ['Baboon', 'Bear'],
#    'C': ['Cat', 'Cougar'],
#    'G': ['Giraffe'],
#    'L': ['Lion'],
#    'Z': ['Zebra']
# }

# 7. Add a method get_groups():
# This method prints the grouped animals as created by sort_animals().
# Example output:
# B: ['Baboon', 'Bear']
# C: ['Cat', 'Cougar']
# G: ['Giraffe']
    def get_groups(self):
        if hasattr(self, 'grouped_animals'):
            print("Grouped animals:")
            for letter, animals in self.grouped_animals.items():
                print(f"{letter}: {animals}")
        else:
            print("No grouped animals found. Please run sort_animals() first.")

# Step 2: Create a Zoo instance
brooklyn_safari = Zoo("Brooklyn Safari")


# Step 3: Use the Zoo methods
brooklyn_safari.add_animal("Giraffe")
brooklyn_safari.add_animal("Bear")
brooklyn_safari.add_animal("Baboon")
brooklyn_safari.get_animals()
brooklyn_safari.sell_animal("Bear")
brooklyn_safari.get_animals()
brooklyn_safari.sort_animals()
brooklyn_safari.get_groups()