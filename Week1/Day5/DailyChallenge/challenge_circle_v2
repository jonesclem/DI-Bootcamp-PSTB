import math
import turtle
# myTurtle = turtle.Turtle()
# myTurtle.circle(50)
# turtle.getscreen()._root.mainloop()

class Circle:
    def __init__(self,radius,diameter=None):
        self.radius = radius
        self.diameter = diameter
        self.list_circles = []

    def get_radius(self):
        return self.radius
    
    def get_diameter(self):
        return self.diameter
    
    def calc_area(self):
        return (math.pi * self.radius) **2
    
    def __printAttributes__(self):
        print(self.get_radius,self.get_diameter)
    
    def __addTwoCircles__(self,other_circle):
        new_radius = self.radius + other_circle.radius
        new_circle = Circle(new_radius)
        return new_circle
    
    def __compareTwoCircles__(self,other_circle):
        if self.radius > other_circle.radius:
            return True
        else:
            return False
    def __isequal__(self,other_circle):
        if self.radius == other_circle.radius:
            return True
        else:
            return False
    def sort(self):
        self.list_circles.append(self)
        return sorted(self.list_circles, key=lambda self: self.radius, reverse=True)
        
        
    
# Test program

circle1 = Circle(15)
circle2 = Circle(25)

print(circle1.calc_area())
circle3 = circle1.__addTwoCircles__(circle2)
print(circle3.radius)
print(circle1.__compareTwoCircles__(circle3))
print(circle1.__isequal__(circle3))
circle2.sort()
list = circle1.sort()
for i in list:
    print(i.radius)

# Test Turtle

myTurtle = turtle.Turtle()
myTurtle.circle(circle1.radius)
turtle.getscreen()._root.mainloop()