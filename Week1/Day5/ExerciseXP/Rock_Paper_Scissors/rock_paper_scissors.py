###### WEEK - DAY 5 - MINI PROJECT - rock_paper_scissors.py

import game as mygame

# Part II - rock-paper-scissors.py

# rock-paper-scissors.py : create 3 functions
# 1. get_user_menu_choice() - this should display a simple menu, get the user’s choice 
# (with data validation), and return the choice. No looping should occur here.
#  The possibles choices are : Play a new game or Show scores or Quit
def get_user_menu_choice():
    while True:
        print("\nMenu:")
        print("1. Play a new game")
        print("2. Show scores")
        print("3. Quit")
        choice = input("Enter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Invalid choice. Please try again.")

# 2. print_results(results) – this should print the results of the games played. It should have a single parameter 
# named results; which will be a dictionary of the results of the games played. It should display these results in
# a user-friendly way, and thank the user for playing.
# Note: results should be in this form: {win: 2,loss: 4,draw: 3}. Bear in mind that this dictionary will need to be 
# created and populated in some other part of our code, 
# and passed in to the print_results function at the right time.

def print_results(results):
    print("\nGame Results:")
    print(f"You won {results['win']} times")
    print(f"You lost {results['loss']} times")
    print(f"You drew {results['draw']} times")
    print("Thank you for playing!")


# 3. main() - the main function. It should take care of 3 things:

#  1.Displaying the menu repeatedly, until the user types in the value to exit the program: ‘x’ or ‘q’,
#  whatever you decide. (Make use of the get_user_menu_choice function)

#  2.When the user chooses to play a game:
#  Create a new Game object (see below), and call its play() function, receiving the result of the game that is returned.
#  Remember the results of every game that is played.

#  3.When the user chooses to exit the program, call the print_results function in order to display a summary of all
#  the games played.


def main():
    game = mygame.Game()
    results = {"win": 0, "loss": 0, "draw": 0}

    while True:
        choice = get_user_menu_choice()
        if choice == '1':
            result = game.play()
            results[result] += 1
        elif choice == '2':
            print_results(results)
        elif choice == '3':
            print_results(results)
            print("Exiting the game. Goodbye!")
            break


if __name__ == "__main__":
    main()