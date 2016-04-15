import sys
import re

lines = [line.rstrip('\r\n') for line in
         open('C:\Users\Atreya\PycharmProjects\Bayesian_NW\HW3_samples_updated\HW3_samples\sample01.txt')]
bn = {}
startLine = ""
Part0 = ""
Part1 = ""
bnObj = {}
parents = []
TruthMaps = {}
i = 0
j = 0
for line in lines:

    line = ' '.join(line.split())
    line = line.rstrip("\r\n")
    # sys.stdout.write(line)
    if line.find("*") == 0 or len(startLine) != 0 or j > 0:
        # facts[j]=line
        if len(startLine) == 0 and j == 1:
            startLine = line.split("|")[0]  # check if j=1 on line.split("|")[0]
        if line.find("*") == 0:  # j=1
            if len(startLine) != 0:
                parentArray = [parents, TruthMaps]  # Check if these shud be there here only if startLine!=""
                bnObj[startLine.split(" | ")[0]] = [parentArray]
            j = 0
            # facts=[]
            startLine = ""
            parents = []

        prob = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        if len(line.split(" | ")) > 1:
            parents = []
            TruthMaps = {}
            parents.append(line.split(" | ")[1].split(" "))
        elif len(line.split(" | ")) == 1 and line.find("|") == 0:
            parents = []
            TruthMaps = {}
        elif line.find("*") != 0 and line.find(" | ") != 0 and prob != []:
            prob = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            Ops = line.split(prob[0])[1].rstrip("\r\n").replace(" ", "", 1).split(" ")
            Ops = tuple(Ops)
            TruthMaps[Ops] = float(prob[0])
        j = j + 1
        i = i + 1
        # facts[i]=line
        # facts=[]
        i = 0
        # facts[i]=line
parentArray = [parents, TruthMaps]
bnObj[startLine.split(" | ")[0]] = [parentArray]
print bnObj
