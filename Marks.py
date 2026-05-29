A=int(input("Enter a marks A:"))
B=int(input("Enter a marks b:"))
C=int(input("Enter a marks c:"))
D=int(input("Enter a marks D:"))
E=int(input("Enter a marks E:"))
total=A+B+C+D+E
percentage=total/5
print("Total Marks=",total)
print("Percentage=",percentage)
if percentage>=75:
    print("Result is: Distinction")
elif percentage>=60:
    print("Result is: First Class")    
elif percentage>=45:
    print("Result is: Pass")    
else:
    print("Result is: Fail")
