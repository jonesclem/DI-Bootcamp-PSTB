import random
from statistics import mean 

# Exercise 1: Birthday Look-up

# Create a variable called birthdays. Its value should be a dictionary.
# Initialize this variable with the birthdays of 5 people of your choice. For each entry in the dictionary, the key should be the person’s name, and the value should be their birthday. Tip: Use the format "YYYY/MM/DD".
# Print a welcome message for the user. Then tell them: “You can look up the birthdays of the people in the list!”
# Ask the user to give you a person's name and store the answer in a variable.
# Get the birthday of the name provided by the user.
# Print out the birthday with a nicely-formatted message.

birthdays = {
    "Albert Einstein": "1879/03/14",
    "Marie Curie": "1867/11/07",
    "Nelson Mandela": "1918/07/18",
    "Frida Kahlo": "1907/07/06",
    "Leonardo da Vinci": "1452/04/15"
}

print("Welcome! You can look up the birthdays of the people in the list!")
name = input("Please enter a person's name: ")
if name in birthdays:
    print(f"{name}'s birthday is on {birthdays[name]}.")
else:
    print(f"Sorry, we don't have the birthday information for {name}.")
    

# Exercise 2: Birthdays Advanced

# Before asking the user to input a person's name, print out all of the names in the dictionary.
# If the person that the user types is not found in the dictionary, print an error message (“Sorry, we don’t have the birthday information for person's name”).

print("Welcome!")

print("We have the birthdays of the following famous people:\n")

# Print all available names
for person in birthdays:
    print("-", person)


name = input("Please enter a person's name: ")
if name in birthdays:
    print(f"{name}'s birthday is on {birthdays[name]}.")
else:
    print(f"Sorry, we don't have the birthday information for {name}.")

# Exercise 3: Check the index
# Instructions
# Using this variable

# names = ['Samus', 'Cortana', 'V', 'Link', 'Mario', 'Cortana', 'Samus']
# Ask a user for their name, if their name is in the names list, print out the index of the first occurence of the name.

# Example: if input is 'Cortana' we should be printing the index 1

names = ['Samus', 'Cortana', 'V', 'Link', 'Mario', 'Cortana', 'Samus']

your_name = input("Please enter your name: ")
if your_name in names:
    index = names.index(your_name)
    print(f"Your name is found at index: {index}")

# Exercise 4: Double Dice
# Create a function that will simulate the rolling of a dice. Call it throw_dice. It should return an integer between 1 and 6.
# Create a function called throw_until_doubles.
# It should keep throwing 2 dice (using your throw_dice function) until they both land on the same number, i.e., until we reach doubles.
# For example: (1, 2), (3, 1), (5, 5) → then stop throwing, because doubles were reached.
# This function should return the number of times it threw the dice in total. In the example above, it should return 3.
# Create a main function. It should throw doubles 100 times (i.e., call your throw_until_doubles function 100 times), and store the results of those function calls (in other words, how many throws it took until doubles were thrown, each time) in a collection. (What kind of collection? Read below to understand what we will need the data for, and this should help you decide which data structure to use).
# After the 100 doubles are thrown, print out a message telling the user how many throws it took in total to reach 100 doubles.
# Also print out a message telling the user the average amount of throws it took to reach doubles. Round this off to 2 decimal places.
# For example:

# If the results of the throws were as follows (your code would do 100 doubles, not just 3):

# (1, 2), (3, 1), (5, 5)
# (3, 3)
# (2, 4), (1, 2), (3, 4), (2, 2)
# Then my output would show something like this:

# Total throws: 8
# Average throws to reach doubles: 2.67.

def throw_dice() -> int:
    return random.randint(1, 6)

def throw_until_doubles() -> int:
    count = 0
    while True:
        count += 1
        dice1 = throw_dice()
        dice2 = throw_dice()
        # print(f"{count} => Rolled: ({dice1}, {dice2})")
        if dice1 == dice2:
            break
    return count