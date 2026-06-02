candidates = ["Krishna", "Dipak", "Kartik","Mahesh"]
votes = [0, 0, 0, 0]
def display_candidates():
    print("\nCandidates List:")
    
    for i in range(len(candidates)):
        print(i + 1, ".", candidates[i])
def cast_vote():
    display_candidates()
    choice = int(input("Enter candidate number to vote: "))

    if 1 <= choice <= len(candidates):
        votes[choice - 1] += 1
        print("Vote cast successfully!")
    else:
        print("Invalid candidate number!")

def display_results():
    print("\nVoting Results:")
    for i in range(len(candidates)):
        print(candidates[i], ":", votes[i], "votes")

while True:
    print("\n***ONLINE VOTING SYSTEM***")
    print("1. Cast Vote")
    print("2. View Results")
    print("3. Exit")

    option = int(input("Enter your choice: "))

    if option == 1:
        cast_vote()
    elif option == 2:
        display_results()
    elif option == 3:
        print("Thank You!")
        break
    else:
        print("Invalid Choice!")