import sys
import random

def generate(buses, capacity):
    """Generate the outputs of all sizes"""
    students = [str(i) for i in range(1, buses*capacity+1)]
    random.shuffle(students)
    with open("outputs/"+size+".out", "w") as file:
        for bus in range(buses):
            file.write("%s\n" % str(students[bus*capacity:(bus+1)*capacity]))



if __name__ == "__main__":
    size = sys.argv[1]
    if size == "small":
        buses, capacity = 6, 8
    elif size == "medium":
        buses, capacity = 31, 16
    elif size == "large":
        buses, capacity = 20, 48

    generate(buses, capacity)
