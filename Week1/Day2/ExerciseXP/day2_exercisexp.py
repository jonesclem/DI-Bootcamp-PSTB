## Week 1 - Python -Day 2 ##

# Exercise 1: Converting Lists into Dictionaries

# You are given two lists. Convert them into a dictionary where the first list contains the keys and the second list contains the corresponding values.
# Lists:
keys = ['Ten', 'Twenty', 'Thirty']
values = [10, 20, 30]

new_dictionary = dict(zip(keys, values))
print(new_dictionary)

# Exercise 2: Cinemax 
# Write a program that calculates the total cost of movie tickets for a family based on their ages.

#     Family members’ ages are stored in a dictionary.
#     The ticket pricing rules are as follows:
#         Under 3 years old: Free
#         3 to 12 years old: $10
#         Over 12 years old: $15
family = {"rick": 43, 'beth': 13, 'morty': 5, 'summer': 8}
total = 0
#Loop through the family dictionary to calculate the total cost.
for member, age in family.items():
    if age <= 3:
        cost = 0
    elif 3 <= age <= 12:
        cost = 10
    else:
        cost = 15
    print (f'The cost for a {age} years old is {cost}')   #Print the ticket price for each family member.
    total = total + cost # calculate the incremental total
print(total) #Print the total cost at the end.

# Exercise 3: Zara
#Instructions
#Create and manipulate a dictionary that contains information about the Zara brand.

# Create a dictionary called brand with the provided data.

brand ={} # Create the empty brand dictionary
brand["name"] = "Zara" # enter each value
brand["creation_date"] = 1975
brand["creator_name"] = "Amancio Ortega Gaona"
brand["type_of_clothes"] = ["men", "women", "children", "home"]
brand["international_competitors"] = ["Gap", "H&M", "Benetton"]
brand["number_stores"] = 7000
brand["major_color"] = {"France": "blue", "Spain": "red", "US": ["pink", "green"]}
print(brand) # display the populate dictionary

# Change the value of number_stores to 2.
brand["number_stores"] = 2
print (brand) # checking that the dictionary has been updated with updated value

# Print a sentence describing Zara’s clients using the type_of_clothes key.
print (f"Zara sells clothes for: {brand["type_of_clothes"]} ")

# Add a new key country_creation with the value Spain.
brand["country_creation"] = "Spain"
print(brand) # checking if new value spain is added in dictionary

#Check if international_competitors exists and, if so, add “Desigual” to the list.
if "international_competitors" in brand:
    brand["international_competitors"].append("Desigual")
print(brand) # checking if desigual is correctly added to international_competitors

#Delete the creation_date key.
del brand["creation_date"]
print(brand) # check if creation_date is deleted

# Print the last item in international_competitors.
print(f"The last item in international competitors is {brand["international_competitors"][-1]}")
# Print the major colors in the US.
print(brand["major_color"]["US"])
# Print the number of keys in the dictionary.
print(f"The number of keys in the dictionary is: {len((brand.keys()))}")
# Print all keys of the dictionary.
print(list(brand.keys()))

#Bonus : create another dictionary called more_on_zara with creation_date and number_stores. Merge this dictionary with the original brand dictionary and print the result.
more_on_zara = {
    "creation_date": 1975, 
    "number_stores": 7000
}
brand.update(more_on_zara) # update the existing dict with the keys from more_on_zara

print(brand) # display the merged dictionary

#Exercise 4 : Some Geography

#Step 1: Define a Function with Parameters
#Define a function named describe_city().
#This function should accept two parameters: city and country.
#Give the country parameter a default value, such as “Unknown”.
#Step 2: Print a Message
#Inside the function, set up the code to display a sentence like “ is in “.
#Replace <city> and <country> with the parameter values.
#Step 3: Call the Function
#Call the describe_city() function with different city and country combinations.
#Try calling it with and without providing the country argument to see the default value in action.
def describe_city(city, country = "Unknown"):
    print(f"{city} is in {country}.")
describe_city("Reykjavik", "Iceland")
describe_city("Paris")

#Exercise 5 : Random
#Goal: Create a function that generates random numbers and compares them.

#Step 1: Import the random Module
#At the beginning of your script, use import random to access the random number generation functions.
import random

#Step 2: Define a Function with a Parameter
#Create a function that accepts a number between 1 and 100 as a parameter.
def my_random (nb:int):
    if (1 <= nb <= 100): # Create a function that accepts a number between 1 and 100 as a parameter.
        number = random.randint(1, 100) #Inside the function, use random.randint(1, 100) to generate a random integer between 1 and 100.
        if nb == number:
            print("Success!")
        else:
            print(f"Fail! Your number: {nb}, Random number: {number}")
my_random(50)

# Exercise 6 : Let’s create some personalized shirts !
## Instructions
## Goal: Create a function to describe a shirt’s size and message, with default values.
# def make_shirt(size = "large", text = "I love Python"):
#     print(f"The size of the shirt is {size} and the text is {text}.")

# make_shirt() # Call make_shirt() to make a large shirt with the default message.
# make_shirt(size = "medium") # Call make_shirt() to make a medium shirt with the default message.
# make_shirt(size = "small", text = "Hello!")

def make_shirt(size="large", text="I love Python"):
    """Display information about the shirt being made."""
    print(f"The size of the shirt is {size} and the text is {text}.")

# Calls
make_shirt()                          # Default: large, "I love Python"
make_shirt("medium")                  # Medium, default message
make_shirt("small", "Keep it simple") # Custom message
make_shirt(size="small", text="Hello!") # Keyword arguments

#Exercise 7 : Temperature Advice
## Goal: Generate a random temperature and provide advice based on the temperature range.

# Step 1: Create the get_random_temp() Function
# Create a function called get_random_temp() that returns a random integer between -10 and 40 degrees Celsius.

def get_random_temp(month:int) -> float:
    if month in [12, 1, 2]:         # Winter
        return random.uniform(-10, 16)
    elif month in [3, 4, 5]:        # Spring
        return random.uniform(5, 25)
    elif month in [6, 7, 8]:        # Summer
        return random.uniform(15, 35)
    elif month in [9, 10, 11]:      # Autumn
        return random.uniform(5, 20)
    else:
        raise ValueError("Month must be between 1 and 12")
    
# Step 2: Create the main() Function

# Create a function called main(). Inside this function:
# Call get_random_temp() to get a random temperature.
# Store the temperature in a variable and print a friendly message like:
# “The temperature right now is 32 degrees Celsius.”

import random

def get_random_temp(season=None):
    """Return a random temperature depending on the season (if given)."""
    # Step 1 & Bonus Step 5
    if season == "winter":
        return round(random.uniform(-10, 10), 1)
    elif season == "spring":
        return round(random.uniform(5, 20), 1)
    elif season == "summer":
        return round(random.uniform(15, 40), 1)
    elif season == "autumn":
        return round(random.uniform(0, 25), 1)
    else:
        # Default: no season specified
        return round(random.uniform(-10, 40), 1)


def main():
    # Bonus Step 5: Ask user for month and determine season
    month = int(input("Enter the month as a number (1–12): "))

    if month in [12, 1, 2]:
        season = "winter"
    elif month in [3, 4, 5]:
        season = "spring"
    elif month in [6, 7, 8]:
        season = "summer"
    else:
        season = "autumn"

    # Step 2: Get and print temperature
    temperature = get_random_temp(season)
    print(f"\nThe temperature right now is {temperature}°C.")

    # Step 3: Give advice based on temperature
    if temperature < 0:
        print("Brrr, that’s freezing! Wear some extra layers today.")
    elif 0 <= temperature < 16:
        print("Quite chilly! Don’t forget your coat.")
    elif 16 <= temperature < 24:
        print("Nice weather.")
    elif 24 <= temperature < 33:
        print("A bit warm, stay hydrated.")
    else:
        print("It’s really hot! Stay cool.")


# Run the program
main()


#Exercise 8: Pizza Toppings
## Instructions
# Write a loop that asks the user to enter pizza toppings one by one.
# Stop the loop when the user types 'quit'.
# For each topping entered, print:
# "Adding [topping] to your pizza."
# After exiting the loop, print all the toppings and the total cost of the pizza.
# The base price is $10, and each topping adds $2.50.

toppings = []
while True:
    topping = input("Enter a pizza topping (or type 'quit' to finish): ")
    if topping.lower() == 'quit':
        break
    toppings.append(topping)
    print(f"Adding {topping} to your pizza.")

base_price = 10
topping_price = 2.5
total_cost = base_price + len(toppings) * topping_price
print(f"Your pizza toppings: {', '.join(toppings)}")
print(f"The total cost of your pizza is: ${total_cost:.2f}")