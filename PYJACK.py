import random

def create_deck():
    """Generates a standard 52-card deck with values."""
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = []
    
    for suit in suits:
        for rank in ranks:
            # Assign values: face cards = 10, Ace = 11 (adjusted dynamically)
            if rank in ['J', 'Q', 'K']:
                value = 10
            elif rank == 'A':
                value = 11
            else:
                value = int(rank)
            deck.append({'rank': rank, 'suit': suit, 'value': value})
            
    random.shuffle(deck)
    return deck

def calculate_score(hand):
    """Calculates total hand value and handles Ace adjustment (11 -> 1)."""
    score = sum(card['value'] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    
    # Reduce Ace from 11 to 1 if score exceeds 21
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
        
    return score

def display_hand(player_name, hand, hide_second_card=False):
    """Formats and prints the cards nicely in the terminal."""
    if hide_second_card:
        cards_str = f"[{hand[0]['rank']}{hand[0]['suit']}] [Hidden Card]"
        print(f"{player_name}'s Hand: {cards_str}")
    else:
        cards_str = " ".join([f"[{card['rank']}{card['suit']}]" for card in hand])
        print(f"{player_name}'s Hand: {cards_str} | Total: {calculate_score(hand)}")

def play_game():
    print("\n" + "="*35)
    print("      WELCOME TO PYTHON BLACKJACK")
    print("="*35)
    
    deck = create_deck()
    
    # Initial deal
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    # Player's turn
    while True:
        display_hand("Dealer", dealer_hand, hide_second_card=True)
        display_hand("Player", player_hand)
        
        player_score = calculate_score(player_hand)
        if player_score == 21:
            print("\n BlackJack! You hit 21!")
            break
        elif player_score > 21:
            print("\n Bust! You went over 21. Dealer wins!")
            return
            
        action = input("\nWould you like to [H]it or [S]tand? ").strip().lower()
        if action == 'h':
            player_hand.append(deck.pop())
            print("\nYou drew a card...")
        elif action == 's':
            break
        else:
            print("Invalid input! Please type 'H' or 'S'.")

    # Dealer's turn (must hit on 16 or lower)
    print("\n--- Dealer's Turn ---")
    display_hand("Dealer", dealer_hand)
    
    while calculate_score(dealer_hand) < 17:
        print("Dealer hits...")
        dealer_hand.append(deck.pop())
        display_hand("Dealer", dealer_hand)
        
    player_score = calculate_score(player_hand)
    dealer_score = calculate_score(dealer_hand)
    
    # Determine winner
    print("\n" + "-"*35)
    print(f"FINAL SCORES: You: {player_score} | Dealer: {dealer_score}")
    print("-"*35)
    
    if dealer_score > 21:
        print("Dealer busted! YOU WIN! 🎉")
    elif player_score > dealer_score:
        print("YOU WIN! 🎉")
    elif player_score < dealer_score:
        print("Dealer wins! 😞")
    else:
        print("It's a tie (Push)! 👔")

# Main replay loop
if __name__ == "__main__":
    while True:
        play_game()
        again = input("\nPlay another hand? (y/n): ").strip().lower()
        if again != 'y':
            print("Thanks for playing! Goodbye.")
            break
