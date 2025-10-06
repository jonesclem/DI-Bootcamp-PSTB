#Exercise 1: What is the Season?

#Ask the user to input a month (1 to 12).

user_month = int(input("Please enter a month (1-12): "))
#Display the season of the month received:
#Spring runs from March (3) to May (5)
#Summer runs from June (6) to August (8)
#Autumn runs from September (9) to November (11)
#Winter runs from December (12) to February (2)

if user_month in (12, 1, 2):
    print("We are in Winter")
elif user_month in (3, 4, 5):
    print("We are in Spring")
elif user_month in (6, 7, 8):
    print("We are in Summer")
elif 9 <= user_month <= 11:
    print("We are in Autumn")

else:
    print("You've entered an invalid number")

# Exercise 2: For Loop
# Key Python Topics:

#     Loops (for)
#     Range and indexing

# Instructions:
#     Write a for loop to print all numbers from 1 to 20, inclusive.
for i in range(1,21):
    print(i)
#     Write another for loop that prints every number from 1 to 20 where the index is even.

# Loop through numbers from 1 to 20 using range()
for i in range(1, 21):
    # Check if the index (i) is even (if result 0 on modulus div by 2 then its an even nb)
    if i % 2 == 0:
        print(i)


# Exercise 3: While Loop

# Key Python Topics:

#     Loops (while)
#     Conditionals
# Instructions:

#     Write a while loop that keeps asking the user to enter their name.
# Defining my name and user name

my_name = "Clem"
user_name1 = ""
#Creating the infinite loop

while user_name1 != my_name:
    user_name1 = str(input("What is your name?: "))
#     Stop the loop if the user’s input is your name.

# Autre possibilite - ici le if and break pas utile car le while gère auto exit si condition est true
# while my_name != your_name:
#     your_name = str(input("What is your name ? "))
#     if my_name == your_name:
#         break


# Exercise 4: Check the index

# Using this variable:

# names = ['Samus', 'Cortana', 'V', 'Link', 'Mario', 'Cortana', 'Samus']

names = ['Samus', 'Cortana', 'V', 'Link', 'Mario', 'Cortana', 'Samus']

# Ask the user for their name
user_name2 = input("Enter your name: ")

# Check if the user's name is in the list
if user_name2 in names:
    # Find and print the index of the first occurrence
    print(f"{user_name2} is at index {names.index(user_name2)}.")
else:
    print("Your name is not in the list.")


# Exercise 5: Greatest Number
# Ask the user for 3 numbers and print the greatest number.
num1 = int(input("Please enter number 1: "))
num2 = int(input("Please enter number 2: "))
num3 = int(input("Please enter number 3: "))

if num1 >= num2 and num1 >= num3:
    greatest = num1
elif num2 >= num1 and num2 >= num3:
    greatest = num2
else:
    greatest = num3

print(f'The greatest number is {greatest}')

# Exercise 6: Random number

#     Ask the user to input a number from 1 to 9 (including).
#     Get a random number between 1 and 9. Hint: random module.
#     If the user guesses the correct number print a message that says “Winner”.
#     If the user guesses the wrong number print a message that says “Better luck next time.”

import random  # Import the random module

# Ask the user to input a number from 1 to 9
user_guess = int(input("Guess a number between 1 and 9: "))

# Generate a random number between 1 and 9
random_number = random.randint(1, 9)

# Compare the user's guess with the random number
if user_guess == random_number:
    print("Winner 🎉 You guessed it right!")
else:
    print("Better luck next time 😅")
    print("The correct number was:", random_number)

