# Exercise 1 : Geometry
# Instructions
# Write a class called Circle that receives a radius as an argument (default is 1.0).
# Write two instance methods to compute perimeter and area.
# Write a method that prints the geometrical definition of a circle.

class Circle():
    def __init__(self, radius = 1.0):
        self.radius = radius

    def perimeter(self):
        return 2 * 3.14 * self.radius

    def area(self):
        return 3.14 * (self.radius ** 2)

    def definition(self):
        print("Un cercle est l’ensemble des points à égale distance d’un centre.") 

# Exercise 2 : Custom List Class
# Instructions
# Create a class called MyList, the class should receive a list of letters.
# Add a method that returns the reversed list.
# Add a method that returns the sorted list.
# Bonus : Create a method that generates a second list with the same length as mylist. The list should be constructed with random numbers. (use list comprehension).

class MyList():
    def __init__(self, letters):
        self.letters = letters

    def reverse_list(self):
        return self.letters[::-1]

    def sort_list(self):
        return sorted(self.letters)

    def generate_random_list(self):
        import random
        random_list = []
        # random_list = [random.randint(0, 100) for _ in range(len(self.letters))]
        for i in range(len(self.letters)):
            # print(f"Index {i}: {self.letters[i]}")
            random_list.append(random.randint(0, 100))

        return random_list

l1 = MyList(['a', 'b', 'c', 'd', 'e'])
print(l1.reverse_list())
print(l1.sort_list())
print(l1.generate_random_list())