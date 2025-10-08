#### DAILY CHALLENGE - WEEK 1 - DAY 4

'''Goal:
Create a Pagination class that simulates a basic pagination system.

Step 1: Create the Pagination Class

Define a class called Pagination to represent paginated content.
It should optionally accept a list of items and a page size when initialized.

Step 2: Implement the __init__ Method

Accept two optional parameters:
items (default None): a list of items
page_size (default 10): number of items per page

Behavior:

If items is None, initialize it as an empty list.
Save page_size and set current_idx (current page index) to 0.
Calculate total number of pages using math.ceil.

Step 3: Implement the get_visible_items() Method

This method returns the list of items visible on the current page.
Use slicing based on the current_idx and page_size.


Step 4: Implement Navigation Methods

These methods should help navigate through pages:

go_to_page(page_num)
→ Goes to the specified page number (1-based indexing).
→ If page_num is out of range, raise a ValueError.

first_page()
→ Navigates to the first page.

last_page()
→ Navigates to the last page.

next_page()
→ Moves one page forward (if not already on the last page).

previous_page()
→ Moves one page backward (if not already on the first page).

Pages are indexed internally from 0, but user input is expected to start at 1.
All navigation methods (except go_to_page) should return self to allow method chaining.

Bonus
Step 5: Add a Custom __str__() Method**

Step 6: Test Your Code
'''

import math

class Pagination():
    def __init__(self, items=None, page_size=10):
        self.items = items
        self.page_size = page_size

        """If item is non initialise as empty list"""
        if items is None:
            items = []

        self.current_idx = 0
        """Total pages : Number of items / Page Size => We apply ceil, to get to the superior integer"""
        self.total_pages = math.ceil(len(items) / page_size)

    """Return the visible item, according to the page_size specified"""
    def get_visible_items(self):
        first_item = self.current_idx * self.page_size
        last_item = first_item + self.page_size
        return self.items[first_item:last_item]

    """ Implementing navigation methods"""
    
    """ We check the page_num entered by the user
    If the page_num is superior to the max page or inferior to 1 -> Raise an error (1-based indexing)
    For all other page_num entered, we substract 1 to the index"""
    def go_to_page(self, page_num):
        if page_num < 1 or page_num > self.total_pages:
            raise ValueError("The specified page number is out of range.")
        self.current_idx = page_num - 1

    """Accessing First page which has index 0"""
    def first_page(self):
        self.current_idx = 0
        return self
    
    """Accessing Last page which is total number of pages -1"""
    def last_page(self):
        self.current_idx = self.total_pages - 1
        return self
    
    """Accessing next page by verifying if the current index used is lower than total pages -1
    then adding one to the current index"""
    def next_page(self):
        if self.current_idx < self.total_pages - 1:
            self.current_idx += 1
        return self
    """If current page index is superior to O remove 1 from the index to go to previous page"""
    def previous_page(self):
        if self.current_idx > 0:
            self.current_idx -= 1
        return self
    
    """Returning a string displaying the items on the current page, each on a new line."""
    def __str__(self):
        return "\n".join(self.get_visible_items())
    
# Testing the program

"""Defining instances"""
alphabetList = list("abcdefghijklmnopqrstuvwxyz")
p = Pagination(alphabetList, 4)

"""Testing Bonus str method"""
print(str(p))
# Output:
# a
# b
# c
# d

"""Calling other methods"""
print(p.get_visible_items())
# output: ['a', 'b', 'c', 'd']

p.next_page()
print(p.get_visible_items())
# output: ['e', 'f', 'g', 'h']

p.last_page()
print(p.get_visible_items())
# output: ['y', 'z']

p.go_to_page(10)
print(p.current_idx + 1) 
# Raises ValueError "Page nb out of range"

p.go_to_page(0) 
# Raises ValueError due to 1-based indexing