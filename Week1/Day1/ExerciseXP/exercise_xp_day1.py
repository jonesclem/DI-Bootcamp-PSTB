#Week1 - Day1 - ExerciseXP

##Exercise1
message = "Hello world"
for i in range(4):
    print(message)


##Exercise2

a = 99
b = 3
c = 8

print((a**b)*c)

##Exercise3
my_name = "Clem"
name_user = input("Please enter your name: ")

if name_user == my_name:
    print("Waouuu we have the same name!")
else:
    print("Our names are different ;-((((")

##Exercise4

height_user = int(input("What is your height in cm?: "))

if height_user > 145:
    print("You are tall enough to ride!")

else:
    print("You need to grow some more to ride ;-))")

##Exercise5

my_fav_numbers = {14, 11, 23}
my_fav_numbers.add(82)
my_fav_numbers.add(19)
print(my_fav_numbers)
my_fav_numbers.remove(19)
print(my_fav_numbers)

friend_fav_numbers = {13, 20, 34, 50}
our_fav_numbers = my_fav_numbers.union(friend_fav_numbers)
print(our_fav_numbers)

##Exercise6
my_tuple = (1, 2, 3)
#my_tuple[3] = 4 ==> TypeError because tuples are immutable

#Exercise7

basket = ["Banana", "Apples", "Oranges", "Blueberries"]

#1. Remove "Banana" from the list.
basket.remove("Banana")
print(basket)
#2. Remove "Blueberries" from the list.
basket.remove("Blueberries")
print(basket)
#3. Add "Kiwi" to the end of the list.
basket.append("Kiwi")
print(basket)
#4. Add "Apples" to the beginning of the list.
basket.insert(0, "Apples")
print(basket)
#5. Count how many apples are in the basket.
print(basket.count("Apples"))
#6. Empty the basket.
basket.clear()
#7. Print the basket.
print(basket)


##Exercise8
sandwich_orders = ["Tuna sandwich", "Pastrami sandwich", "Avocado sandwich", "Pastrami sandwich", "Egg sandwich", "Chicken sandwich", "Pastrami sandwich"]

#The deli has run out of pastrami, use a while loop to remove 
# all occurrences of Pastrami sandwich from sandwich_orders.

while "Pastrami sandwich" in sandwich_orders:
    sandwich_orders.remove("Pastrami sandwich")

print(sandwich_orders)

#Create an empty list called finished_sandwiches.
finished_sandwiches = []

#One by one, remove each sandwich from the sandwich_orders while adding them to the finished_sandwiches list.
sandwich_orders_two = sandwich_orders[:] #copy of the first list to iterate without skipping items
print(sandwich_orders_two)


for sandwich in sandwich_orders_two:
    finished_sandwiches.append(sandwich)
    sandwich_orders.remove(sandwich)

print(finished_sandwiches)
print(sandwich_orders)

for sandwich in finished_sandwiches:
    print(f'I made your {sandwich}')
