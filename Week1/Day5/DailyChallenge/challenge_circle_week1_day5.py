###### WEEK - DAY 5 - MINI PROJECT - DAILY CHALLENGE CIRCLE

import math
import turtle

# Instructions :
# The goal is to create a class that represents a simple circle.
# A Circle can be defined by either specifying the radius or the diameter.
# The user can query the circle for either its radius or diameter.

# Other abilities of a Circle instance:

# Compute the circle's area
# Print the attributes of the circle - use a dunder method
# Be able to add two circles together, and return a new circle with the new radius - use a dunder method
# Be able to compare two circles to see which is bigger, and return a Boolean - use a dunder method
# Be able to compare two circles and see if there are equal, and return a Boolean- use a dunder method
# Be able to put them in a list and sort them
# Bonus (not mandatory) : Install the Turtle module, and draw the sorted circles

class Circle:
    def __init__(self, radius=None, diameter=None):
        if radius is not None:
            self.radius = radius
        elif diameter is not None:
            self.radius = diameter / 2
        else:
            raise ValueError("You must provide either radius or diameter.")
    
    @property
    def diameter(self):
        return self.radius * 2

    @diameter.setter
    def diameter(self, value):
        self.radius = value / 2

    @property
    def area(self):
        return math.pi * (self.radius ** 2)

    def __repr__(self):
        """Affichage lisible de l'objet."""
        return f"Circle(radius={self.radius:.2f}, diameter={self.diameter:.2f}, area={self.area:.2f})"

    def __add__(self, other):
        """Addition : combine les rayons et renvoie un nouveau cercle."""
        if not isinstance(other, Circle):
            raise TypeError("Tu ne peux additionner qu'un autre Circle.")
        return Circle(radius=self.radius + other.radius)

    def __eq__(self, other):
        """Comparaison d'égalité."""
        return math.isclose(self.radius, other.radius, rel_tol=1e-9)

    def __lt__(self, other):
        """Comparaison stricte (utile pour trier)."""
        return self.radius < other.radius

    def __gt__(self, other):
        return self.radius > other.radius

"""Not mandatory part creating draw_sorted_circles method and using Turtle"""

def draw_sorted_circles(circles):
    """
    Trie les cercles par rayon croissant et les dessine avec turtle.
    Chaque cercle est centré verticalement, espacé horizontalement, et étiqueté.
    """
    if not circles:
        return

    # Tri
    circles = sorted(circles)

    # Prépare la fenêtre
    screen = turtle.Screen()
    screen.title("Cercles triés (Turtle)")
    screen.setup(width=1.0, height=1.0)  # plein écran
    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.pensize(2)

    # Palette simple (rotation des couleurs)
    colors = [
        "black", "red", "blue", "green", "purple", "orange", "brown", "teal", "gray", "magenta"
    ]

    # Calcul des positions pour centrer l’ensemble
    radii = [c.radius for c in circles]
    max_r = max(radii)
    gap = max(20, max_r * 0.6)  # espace minimum entre cercles
    total_width = sum(c.diameter for c in circles) + gap * (len(circles) - 1)

    start_x = -total_width / 2.0
    y_center = 0

    x = start_x
    for i, c in enumerate(circles):
        r = c.radius
        # Position: pour dessiner un cercle centré, turtle.circle(r) part du bord droit.
        # On se place donc au point (x + r, y_center - r).
        cx = x + r
        cy = y_center - r

        # Dessin du cercle
        t.penup()
        t.goto(cx, cy)
        t.setheading(0)
        t.pendown()
        t.pencolor(colors[i % len(colors)])
        t.circle(r)

        # Étiquette sous le cercle
        t.penup()
        t.goto(cx, cy - 20)  # un peu plus bas que le bas du cercle
        t.write(f"r={c.radius:.1f}", align="center", font=("Arial", 12, "normal"))

        # Avance la position x pour le cercle suivant
        x += c.diameter + gap

    # Attente clic pour fermer
    screen.exitonclick()

if __name__ == "__main__":
    c1 = Circle(radius=30)
    c2 = Circle(diameter=120)  # rayon = 60
    c3 = Circle(radius=15)
    c4 = c1 + c3               # rayon = 45
    c5 = Circle(radius=80)

    circles = [c1, c2, c3, c4, c5]
    """Using the Turple module"""
    draw_sorted_circles(circles) 