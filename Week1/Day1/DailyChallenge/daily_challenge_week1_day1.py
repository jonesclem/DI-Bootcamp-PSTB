### Daily Challenge - Week 1 - Day1 ###

##Challenge 1

#Ask the user for a number and a length.

number = int(input("Please enter a number: ")) # ensuring the ask will be saved as an integer
length = int(input("Please enter a length: ")) # ensuring the ask will be saved as an integer

#Create a program that prints a list of multiples of the number until the list length reaches length.

# Create a new empty list that will be filled by the loop
multiples = []

for i in range (1, length+1): # creating a loop iteration in a range from 1 to length+1 to ensure its runs on full chosen length
    multiples.append(number * i) # for each iteration add the multiple of the chosen number in the list

#multiples = [num * i for i in range (1, length + 1)]

# display the result list
print(multiples)


##Challenge 2

# >> Write a program that asks a string to the user, and display a new string with any duplicate consecutive letters removed.

# Ask the user for a string
str_user = input("Please enter a string: ") 

# Create a new empty string that will be filled by the loop
new_str = ""

for char in str_user: # check each character of the string entered by the user
    if not new_str or char != new_str[-1]:   # check if the character already exists and compare with only the last char added
        new_str += char # add the char in the new_str

# Show the result
print("String without consecutive duplicates:", new_str)