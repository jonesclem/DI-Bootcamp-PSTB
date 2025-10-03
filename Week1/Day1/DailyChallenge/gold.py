from datetime import datetime

# Ask for user birthdate
birthdate_str = input("Enter your birthdate (DD/MM/YYYY): ")

# Convert string to datetime object
birthdate = datetime.strptime(birthdate_str, "%d/%m/%Y")

# Get today's date
today = datetime.today()

# Calculate age
age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Get last digit of age
candles_count = age % 10
if candles_count == 0:
    candles_count = 1  # At least 1 candle, if age ends with 0

# Build candles string
candles = "i" * candles_count
padding = (11 - candles_count) // 2   # center candles in 11 spaces
candles_line = " " * padding + candles + " " * (11 - candles_count - padding)

# Print cake
print(f"   ___{candles_line}___")
print("  |:H:a:p:p:y:|")
print("__|___________|__")
print("|^^^^^^^^^^^^^^^^^|")
print("|:B:i:r:t:h:d:a:y:|")
print("|                 |")
print("~~~~~~~~~~~~~~~~~~~")

# Print extra info
print(f"\n🎉 You are {age} years old!")