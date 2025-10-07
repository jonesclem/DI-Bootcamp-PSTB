# Exercise 3 : Restaurant Menu Manager
# Instructions
# The purpose of this exercise is to create a restaurant menu. The code will allow a manager to add and delete dishes.
# Create a python file called menu_manager.py.
# Create a class called MenuManager.
# Create a method __init__ that instantiates an attribute called menu. The menu attributes value will be all the current dishes (list of dictionaries). 
# Each dish will be stored in a dictionary where the keys are name, price, spice level and gluten index (which value is a boolean).
# Here is a list of the dishes currently on the menu:
#     Soup – 10 – B - False
#     Hamburger – 15 - A - True
#     Salad – 18 - A - False
#     French Fries – 5 - C - False
#     Beef bourguignon– 25 - B - True
#     Meaning: For the spice level:
#        • A = not spicy,
#        • B = a little spicy,
#        • C = very spicy
# The dishes provided above should be the value of the menu attribute.
# Create a method called add_item(name, price, spice, gluten). This method will add new dishes to the menu.
# Create a method called update_item(name, price, spice, gluten). This method checks whether a dish is in the menu, if the dish exists then update it. 
# If not notify the manager that the dish is not in the menu.
# Create a method called remove_item(name). This method should check if the dish is in the menu, if the dish exists then delete it and print the updated dictionary. 
# If not notify the manager that the dish is not in the menu.

class MenuManager:
    def __init__(self):
        self.menu = [
            {"name": "Soup", "price": 10, "spice": "B", "gluten": False},
            {"name": "Hamburger", "price": 15, "spice": "A", "gluten": True},
            {"name": "Salad", "price": 18, "spice": "A", "gluten": False},
            {"name": "French Fries", "price": 5, "spice": "C", "gluten": False},
            {"name": "Beef bourguignon", "price": 25, "spice": "B", "gluten": True}
        ]

    def add_item(self, name, price, spice, gluten):
        new_dish = {"name": name, "price": price, "spice": spice, "gluten": gluten}
        self.menu.append(new_dish)
        print(f"Added {name} to the menu.")

    def update_item(self, name, price, spice, gluten):
        for dish in self.menu:
            if dish["name"] == name:
                dish["price"] = price
                dish["spice"] = spice
                dish["gluten"] = gluten
                print(f"Updated {name} in the menu.")
                return
        print(f"{name} is not in the menu.")

    def remove_item(self, name):
        for dish in self.menu:
            if dish["name"] == name:
                self.menu.remove(dish)
                print(f"Removed {name} from the menu.")
                print("Updated menu:", self.menu)
                return
        print(f"{name} is not in the menu.")

my_menu = MenuManager()
my_menu.add_item("Pizza", 12, "B", True)
my_menu.update_item("Salad", 20, "A", False)
my_menu.remove_item("Soup")
my_menu.remove_item("Pasta")  # This dish does not exist