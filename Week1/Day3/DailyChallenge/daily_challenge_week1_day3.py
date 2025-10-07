## Daily challenge: Old MacDonald’s Farm - Week 1 - Day 3

# Instructions: Old MacDonald’s Farm
# You are given example code and output. Your task is to create a Farm class that produces the same output. 

# Step 1: Create the Farm Class

#     Create a class called Farm.
#     This class will represent a farm and its animals.
class Farm():

# Step 2: Implement the __init__ Method
#     The Farm class should have an __init__ method.
#     It should take one parameter: farm_name.
#     Inside __init__, create two attributes: name to store the farm’s name and animals to store the animals (initialize as an empty dictionary).
    def __init__(self, farm_name):
        self.name = farm_name # defining the attribute farm's name
        self.animals = {} # initializing empty dictionary

# Step 3: Implement the add_animal Method
#     Create a method called add_animal.
#     It should take two parameters: animal_type and count (with a default value of 1). 
#     Count is the quantity of the animal that will be added to the animal dictionary.
#     The dictionary will look like this:
# {'cow': 1, 'pig':3, 'horse': 2}

    def add_animal(self, animal_type, count = 1):
        #     If the animal_type already exists in the animals dictionary, increment its count by count.
        if animal_type in self.animals:
            self.animals[animal_type] += count
        #     If it doesn’t exist, add it to the dictionary as the key and with the given count as value.
        else:
            self.animals[animal_type] = count
        # here we could print the dictionary iteration to check if it's well formatted
        #print(self.animals)

# Step 4: Implement the get_info Method

#   Create a method called get_info.
#   It should return a string that displays the farm’s name, the animals and their counts, and the “E-I-E-I-0!” phrase.
#   Format the output to match the provided example.
#   Use string formatting to align the animal names and counts into columns.
    def get_info(self):
        info = f"{self.name}'s farm\n\n"
        for animal, count in self.animals.items():
            info += f"{animal} : {count}\n"
        info += "\n\tE-I-E-I-0!"
        return info

# Step 5: Test Your Code
#     Create a Farm object and call the add_animal and get_info methods.
#     Verify that the output matches the provided example.

# macdonald = Farm("McDonald")
# macdonald.add_animal('cow', 5)
# macdonald.add_animal('sheep')
# macdonald.add_animal('sheep')
# macdonald.add_animal('goat', 12)
# print(macdonald.get_info())

# Bonus: Expand The Farm
# Step 6: Implement the get_animal_types Method
#  Add a method called get_animal_types to the Farm class.
#  This method should return a sorted list of all animal types (keys from the animals dictionary).
#  Use the sorted() function to sort the list.
    def get_animal_types(self):
        return sorted(self.animals.keys())

# Step 7: Implement the get_short_info Method

#  Add a method called get_short_info to the Farm class.
#  This method should return a string like “McDonald’s farm has cows, goats and sheeps.”.
#  Call the get_animal_types method to get the list of animals.
#  Construct the string, adding an “s” to the animal name if its count is greater than 1.
#  Use string formatting to create the output.

    def get_short_info(self):
        animal_types = self.get_animal_types()
        animal_list = []
        for animal in animal_types:
            if self.animals[animal] > 1:
                animal_list.append(animal + "s") #Adding an "s" to pluralize the animal name
            else:
                animal_list.append(animal)
        if len(animal_list) > 1:
            animal_str = ", ".join(animal_list[:-1]) + " and " + animal_list[-1]
        else:
            animal_str = animal_list[0]
        return f"{self.name}'s farm has {animal_str}."
    
macdonald = Farm("McDonald")
macdonald.add_animal('cow', 5)
macdonald.add_animal('sheep')
macdonald.add_animal('sheep')
macdonald.add_animal('goat', 12)
print(macdonald.get_info())
print(macdonald.get_animal_types())
print(macdonald.get_short_info())