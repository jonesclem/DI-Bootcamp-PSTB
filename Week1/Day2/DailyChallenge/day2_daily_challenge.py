## Daily Challenge Week 1 - Day 2

# Challenge
# Ask a user for a word.
user_word = input("Please enter a word : ")

# Convert to lowercase for case-insensitivity
user_word = user_word.lower()

# Write a program that creates a dictionary. This dictionary stores the indexes of each letter in a list.
# Make sure the letters are the keys.
# Make sure the letters are strings.
# Make sure the indexes are stored in a list, and those lists are values.
user_dict = {}

for index, letter in enumerate(user_word): # iterates over the characters of user_word to return pairs of index and letters
    # Only consider alphabetic letters (ignore spaces, digits, punctuation, etc.)
    if letter.isalpha():
        if letter in user_dict: # check if letter already exists as a key in the dictionary
            user_dict[letter].append(index) # if condition true add the index of the letter to dictionary
        else:
            user_dict[letter] = [index] #If this is the first time we see that letter, create a new key in the dictionary with a single-item list containing the current index.

# Examples
# “dodo” ➞ { “d”: [0, 2], “o”: [1, 3] }
# “froggy” ➞ { “f”: [0], “r”: [1], “o”: [2], “g”: [3, 4], “y”: [5] }
# “grapes” ➞ { “g”: [0], “r”: [1], “a”: [2], “p”: [3], “e”: [4], “s”: [5] } 

# Display the result
print("\nLetter positions (case-insensitive, letters only):")
print(user_dict)