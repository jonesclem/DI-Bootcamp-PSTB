import re

my_matrix = """7ii
Tsx
h%?
i #
sM 
$a 
#t%
^r!"""

matrix = [list(row) for row in my_matrix.split('\n')]
result = ''.join(''.join(row[i] for row in matrix) for i in range(len(matrix[0])))
print(result)

letters = re.findall(r'[A-Za-z]+', result)
secret_message = ' '.join(letters)
print(secret_message)