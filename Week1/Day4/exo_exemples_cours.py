
#### WEEK 1 DAY 4 ###3

###INHERITANCE

# class Animal():
#     def __init__(self, type, number_legs, sound):
#         self.type = type
#         self.number_legs = number_legs
#         self.sound = sound

#     def make_sound(self):
#         print(f"I am an animal, and I love saying {self.sound}")

# class Dog(Animal):
#     pass

# rex= Dog("dog", 4, "wouaf")
# print('This animal is a:', rex.type)
# # >> This animal is a dog

# print('This dog has', rex.number_legs , ' legs')
# # >> This dog has 4 legs

# print('This dog makes the sound ', rex.sound)
# # >> This dog makes the sound wouaf

# rex.make_sound()
# # >> I am an animal, and I love saying wouaf

# ##########################

# class Animal():
#     def __init__(self, type, number_legs, sound):
#         self.type = type
#         self.number_legs = number_legs
#         self.sound = sound

#     def make_sound(self):
#         print(f"I am an animal, and I love saying {self.sound}")

# class Dog(Animal):
#     def fetch_ball(self):
#         print("I am a dog, and I love fetching balls")

# rex = Dog('dog', 4, "Wouaf")
# print('This animal is a:', rex.type)
# # >> This animal is a dog

# rex.fetch_ball()
# # >> I am a dog, and I love fetching balls

# roger = Animal('Roger', 4, "Grr")
# roger.fetch_ball()
# # >> AttributeError: 'Animal' object has no attribute 'fetch_ball'

########################

class Circle:
    color = "red"

class NewCircle(Circle):
    color = "blue"

nc = NewCircle
print(nc.color)
# >> What will be the output ?