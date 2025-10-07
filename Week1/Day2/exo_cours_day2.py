dico = {}

while True:
    key = input("Enter key or quit to stop: ")
    if key.lower() == "quit":
        break
    value = input("Enter value:")
dico[key] = value

print(dico)