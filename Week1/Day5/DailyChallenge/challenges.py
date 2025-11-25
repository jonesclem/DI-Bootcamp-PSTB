###### WEEK - DAY 5 - MINI PROJECT - DAILY CHALLENGE CHALLENGES

# Challenge 1 : Sorting

# Instructions
# Write a program that accepts a comma separated sequence of words as input and prints the words in a comma-separated sequence after sorting them alphabetically.
#  Use List Comprehension
# Example:
# Suppose the following input is supplied to the program: without,hello,bag,world
# Then, the output should be: bag,hello,without,world

def sort_words(input_string):
    # Split the input string into a list of words
    words = input_string.split(',')
    
    # Sort the list of words alphabetically using list comprehension
    sorted_words = sorted([word.strip() for word in words])
    
    # Join the sorted list back into a comma-separated string
    output_string = ','.join(sorted_words)
    
    return output_string

# Challenge 2 : Longest Word
# Instructions

# Write a function that finds the longest word in a sentence. If two or more words are found, return the first longest word.
# Characters such as apostrophe, comma, period count as part of the word (e.g. O’Connor is 8 characters long).

# Examples
# longest_word("Margaret's toy is a pretty doll.") ➞ "Margaret's"
# longest_word("A thing of beauty is a joy forever.") ➞ "forever."
# longest_word("Forgetfulness is by all means powerless!") ➞ "Forgetfulness"

def longest_word(sentence):
    # Split the sentence into words
    words = sentence.split()
    
    # Initialize variables to track the longest word and its length
    longest = ""
    max_length = 0
    
    # Iterate through each word in the list
    for word in words:
        # Check if the current word's length is greater than the max_length found so far
        if len(word) > max_length:
            longest = word
            max_length = len(word)
    
    return longest

if __name__ == "__main__": # Important if you want to import the functions from somewhere else
    # challenge 1
    input_string = "without,hello,bag,world"
    print(sort_words(input_string))  # Output: bag,hello,without,world

    # challenge 2

    print(longest_word("Margaret's toy is a pretty doll.")) # "Margaret's"
    print(longest_word("A thing of beauty is a joy forever.")) # "forever."
    print(longest_word("Forgetfulness is by all means powerless!")) # "Forgetfulness"