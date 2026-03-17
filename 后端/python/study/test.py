# create a sample collection 
users = { "hans":"active", "peter":"inactive", "michael":"active" }

## iterate over a copy

# for user , status in users.copy().items():
#     if status == "inactive":
#         del users[user]

      

# active_users = { }

# for user , b in users.items():
#     if b == "inactive":
#         active_users[user] = b

# print(users)
# print(active_users)


# list(range(5, 10))
# print(list(range(0, 100, 3)))

# print(sum(range(0, 100, 3)))


# from enum import Enum
# class Color(Enum):
#     RED = 'red'
#     GREEN = 'green'
#     BLUE = 'blue'

# color = Color(input("Enter your choice of 'red', 'blue' or 'green': "))

def fib(n):
    a,b = 0,1
    while a < n:
        print(a, end=' ')
        a,b = b, a+b

fib(2000)