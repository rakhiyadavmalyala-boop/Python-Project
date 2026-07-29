import random
while True:
    user = input("Roll the dice? (y/n): ").strip().lower()
    if user == "y":
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        print(f"({dice1}, {dice2})")
    elif user == "n":
        print("Thank you for playing!")
        break
    else:
        print("Invalid input. Please enter 'y' or 'n'.")
