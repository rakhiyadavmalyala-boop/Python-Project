import random

# Mapping choices to display names and emojis
CHOICES = {
    'r': ('Rock', '🪨'),
    'p': ('Paper', '📄'),
    's': ('Scissors', '✂️')
}

def get_user_choice():
    while True:
        user_input = input("Choose (r)ock, (p)aper, (s)cissors, or (q)uit: ").strip().lower()
        if user_input in CHOICES or user_input == 'q':
            return user_input
        print("Invalid input. Please enter 'r', 'p', 's', or 'q'.")

def play_game():
    player_score = 0
    computer_score = 0
    draws = 0

    print("=== Welcome to Rock-Paper-Scissors! ===")

    while True:
        user_choice = get_user_choice()
        if user_choice == 'q':
            print("\nThanks for playing!")
            print(f"Final Score -> You: {player_score} | Computer: {computer_score} | Draws: {draws}")
            break

        computer_choice = random.choice(list(CHOICES.keys()))
        
        user_name, user_emoji = CHOICES[user_choice]
        comp_name, comp_emoji = CHOICES[computer_choice]

        print(f"\nYou chose: {user_name} {user_emoji}")
        print(f"Computer chose: {comp_name} {comp_emoji}")

        if user_choice == computer_choice:
            print("It's a tie! 🤝")
            draws += 1
        elif (user_choice == 'r' and computer_choice == 's') or \
             (user_choice == 'p' and computer_choice == 'r') or \
             (user_choice == 's' and computer_choice == 'p'):
            print("You win this round! 🎉")
            player_score += 1
        else:
            print("Computer wins this round! 💻")
            computer_score += 1

        print(f"Score: You {player_score} - {computer_score} Computer (Draws: {draws})\n")

if __name__ == "__main__":
    play_game()
