import re
DECISION_VAR_LIST=[]
bayes_network={}

queriesMap={}
def read_file_data(file_handler):
    queries = []
    all_vars = []
    utility = []
    while True:
        query_str = str(file_handler.readline().rstrip())
        if query_str == "******":
            break
        queries.append(query_str)

    bayes_network = {}
    while True:
        line = str(file_handler.readline().rstrip())
        if line == "******" or line == '':
            break
        if line == "***":
            continue
        arr = line.split(' | ')
        if len(arr) > 1:
            key = arr[0]
            all_vars.insert(0, key)
            local_dict = {}
            parents = arr[1].split(' ')
            for i in range(2 ** len(parents)):
                bn_table_line = str(file_handler.readline().rstrip())
                bn_table_arr = bn_table_line.split(' ', 1)
                local_dict[tuple(bn_table_arr[1].split(' '))] = float(bn_table_arr[0])
            bayes_network[key] = [parents, local_dict]
        else:
            key = arr[0]
            all_vars.insert(0, key)
            local_dict = {}
            prob_value = file_handler.readline().rstrip('\r\n')
            if prob_value.isdigit():
                local_dict[None] = float(prob_value)
            else:
                DECISION_VAR_LIST.append(key)
                local_dict[None] = float(prob_value)
            bayes_network[key] = [[], local_dict]

    while True:
        line = str(file_handler.readline().rstrip())
        if line == '':
            break
        arr = line.split(' | ')
        if len(arr) > 1:
            another_local_dict = {}
            util_dependency_nodes = arr[1].split(' ')
            utility.append(util_dependency_nodes)
            for i in range(2 ** len(util_dependency_nodes)):
                util_val_line = str(file_handler.readline().rstrip())
                util_val_arr = util_val_line.split(' ', 1)
                another_local_dict[tuple(util_val_arr[1].split(' '))] = float(util_val_arr[0])
            utility.append(another_local_dict)
    return queries, bayes_network, utility, all_vars
'''
def __init__(self, fname):
    self.net = {}
    self.queries = []
    lines = []  # buffer
    with open(fname) as f:
        for line in f:
            lines.append(line)
        self._parse(lines)

def _parse(self, lines):
    qFlag = True
    for line in lines:
        if line == "******\n":
            qFlag = False
            continue
        if qFlag is True:
            lhs,rhs = self.objParse.getParams(line)
            if len(rhs)>0:
                queryFromFile.append(lhs+rhs)
            else:
                queryFromFile.append(lhs)

        else:
            pass
  #  print queries
    #print bayes_network
   # print all_vars
  #  print utility

'''



# start reading from the bottom of the file up.


# my debug print function.  if I want debug messages printed, then
# print(args), otherwise do nothing.  this is nice so I can leave my
# debug statements in and just have them print when I want them.
def debugprint(*args):
    pass
    #print(args)


# compute probability that var has the value val.  e are the list of
# variable values we already know, and bn has the conditional probability
# tables.
def Pr(var, val, e, bn):
    parents = bn[var][0]
    debugprint('Pr***', var, val, e, bn, parents)
    if len(parents) == 0:
        truePr = bn[var][1][None]
    else:
        debugprint('   Pr***')
        parentVals = [e[parent] for parent in parents]
        truePr = bn[var][1][tuple(parentVals)]
    if val=='+': return truePr
    else: return 1.0-truePr


# QX is a dictionary that have probabilities for different values.  this
# function normalizes so the probabilities all add up to 1.
def normalize(QX):
    total = 0.0
    for val in QX.values():
        total += val
    for key in QX.keys():
        QX[key] /= total
    return QX


# The enumerate-ask function from the textbook that does the variable
# enumeration algorithm to compute probabilities in a Bayesian network.
# Remember this is exponential in the worst case!
#
# Note: in both this function and enumerateAll, I make sure to undo any
# changes to the dictionaries and lists after I am done with recursive
# calls.  This is needed because dictionaries and lists are passed by
# reference in python.  Instead of the undoing, I could use deep copy.
def enumerationAsk(X, e, bn,varss):
    QX = {}
    for xi in ['-','+']:
        e[X] = xi
        QX[xi] = enumerateAll(varss,e,bn)
        del e[X]
    #return QX
    return normalize(QX)

def getParams(line):
        line = line.strip()
        type = ''
        lhs = {}
        rhs = {}
        line = line[:-1]
        arr = line.split("(")
        type = arr[0].strip()
        params = arr[1].split("|")
        lhsArr = params[0].split(',')
        for lhsEnt in lhsArr:
            temp = lhsEnt.split('=')
            lhs[temp[0].strip()] = temp[1].strip();

        if (len(params) > 1):
            rhsArr = params[1].split(',')
            for rhsEnt in rhsArr:
                temp = rhsEnt.split('=')
                rhs[temp[0].strip()] = temp[1].strip();
        return lhs,rhs

def LHRSparse( lines):

    qFlag = True
    for line in lines:
        if line == "******\n":
            qFlag = False
            continue
        if qFlag is True:
            lhs,rhs = getParams(line)
            if len(str(rhs))!=0:
                queriesMap[str(lhs)]=rhs
            else:
                queriesMap[str(lhs)]=lhs
        else:
            pass

def GetLRHS(fname):
        net = {}

        lines = []  # buffer
        with open(fname) as f:
            for line in f:
                lines.append(line)
                LHRSparse(lines)


# Helper function for enumerateAsk that does the recursive calls,
# essentially following the tree that is in the book.
def enumerateAll(varss, e,bn):
    debugprint('EnumerateAll***', varss, e, bn)
    if len(varss) == 0: return 1.0
    Y = varss.pop()
    if Y in e:
        val = Pr(Y,e[Y],e,bn) * enumerateAll(varss,e,bn)
        varss.append(Y)
        return val
    else:
        total = 0
        e[Y] = '+'
        total += Pr(Y,'+',e,bn) * enumerateAll(varss,e,bn)
        e[Y] = '-'
        total += Pr(Y,'-',e,bn) * enumerateAll(varss,e,bn)
        del e[Y]
        varss.append(Y)
        return total


# put the conditional probability tables for the Bayesian network into
# a dictionary.  The key is a string describing the node.
#
# The value for the key has the information about its parents and the
# conditional probabilities.  It is a list with two things.  The first
# thing is a list of the nodes parents (an empty list if there are no
# parents).  The second thing is the conditional probability table in a
# dictionary; the key to this dictionary is values for the parents, and the
# value is the probability of being '+' given these values for the parents.
'''bn = {'Burglary':[[],{None:.001}],
      'Earthquake':[[],{None:.002}],
      'Alarm':[['Burglary','Earthquake'],
               {('-','-'):.001,('-','+'):.29,
                ('+','-'):.94,('+','+'):.95}],
      'JohnCalls':[['Alarm'],
                   {('-',):.05,('+',):.90}], #note: ('-',) is a tuple with just the value '-'.  ('-') would not be, python makes that just '-', and that would not be good because the code above assumes it is a tuple.
      'MaryCalls':[['Alarm'],
                   {('-',):.01,('+',):.70}]} '''


#bn = {'NightDefense': [['LeakIdea'], {('+',): 0.8, ('-',): 0.3}], 'LeakIdea': [[], {None: 0.4}], 'Demoralize': [['NightDefense', 'Infiltration'], {('-', '+'): 0.95, ('-', '-'): 0.05, ('+', '-'): 0.6, ('+', '+'): 0.3}], 'Infiltration': [[], {None: 0.5}]}

# a list of the variables, starting "from the bottom" of the network.
# in the enumerationAsk algorithm, it will look at the variables from
# the end of this list first.
#varss = ['Demoralize','NightDefense','Infiltration','LeakIdea']
GetLRHS('C:\Users\Atreya\PycharmProjects\Bayesian_NW\HW3_samples_updated\HW3_samples\sample01.txt')
queries, bayes_network, utility, all_vars=read_file_data(open('C:\Users\Atreya\PycharmProjects\Bayesian_NW\HW3_samples_updated\HW3_samples\sample01.txt'))
#print bayes_network

bn=bayes_network
#print queries.split(",")[0].split("=")[0]
#print utility
valueMap={}
for key, value in queriesMap.iteritems():
    val=1.0
    if len(value)==0:

        keysplit=key.split(",")
        sign="".join(re.findall("\+",keysplit[0].split(":")[1]))
        if (len(sign)==0):
           sign= "".join(re.findall("\-",keysplit[0].split(":")[1]))
        for splt in keysplit:
            word = "".join(re.findall("[a-zA-Z]+", splt))
            val*=float(enumerationAsk(word,value,bn,all_vars)[sign])
    else:
        val=1
        keysplit=key.split(",")
        sign="".join(re.findall("\+",keysplit[0].split(":")[1]))
        if (len(sign)==0):
           sign= "".join(re.findall("\-",keysplit[0].split(":")[1]))
        for splt in keysplit:
            word = "".join(re.findall("[a-zA-Z]+", splt))
            val*=float(  enumerationAsk(word,value,bn,all_vars)[sign])
    print val

'''
#print(enumerationAsk(queriesMap,bn,all_vars))
# call the enumerationAsk function to figure out a probability.
#val1=enumerationAsk('Demoralize',{'LeakIdea':'+','Infiltration':'+','NightDefense':'+'},bn,varss)
#val2=enumerationAsk('Demoralize',{'LeakIdea':'+','Infiltration':'-','NightDefense':'+'},bn,varss)
#val3=enumerationAsk('NightDefense',{'LeakIdea':'+','Infiltration':'+'},bn,varss)

#val4=enumerationAsk('LeakIdea',{'LeakIdea':'+','Infiltration':'+','NightDefense':'-'},bn,varss)
#print(val1)
#print(val2)
#print(val3)
#print(val4)




# ***
# Now this part of the file has some code to do random sampling to estimate
# probabilities in a Bayes Net.
# ***

import random

# obtain a random sample from the bayes net.  this will return values
# for all of the variables that are sampled according to the probabilities
# in the bayes net.  the varss list is a list of the variables in order
# from "bottom to top", so we'll start looking at the variables from the
# end - we sample the parents before the children.
def priorSample(bn, varss):
    # first reverse variables so they are top down.
    varss.reverse()

    # e will keep track of values for the variables
    e = {}
    for var in varss:
        # pick a value for var according to the probabilities in bn and the
        # ones we already picked.

        # probability it is '+'.
        prTrue = Pr(var,'+',e,bn)

        # then set it to '+' with prTrue and '-' otherwise.
        if random.uniform(0.0,1.0) <= prTrue:
            e[var] = '+'
        else:
            e[var] = '-'

    # reverse variable list again so it is the same as it was before this
    # function was called.
    varss.reverse()

    # return the sample - e
    return e

#print(priorSample(bn,varss))


# see if the two sets of variable settings are consistent
def consistent(e1, e2):
    for k in e1:
        if k in e2 and e1[k] != e2[k]: return '-'
    return '+'


# do rejection sampling.  So take samples to estimate the probability
# that X is '+' or '-' given the values of variables that are already
# known in e.  Take N many samples.
def rejectionSample(X,bn,e,num,varss):
    N = {'+':0, '-':0}
    for i in range(0, num):
        sample = priorSample(bn,varss)
        if consistent(sample,e):
            N[sample[X]] += 1
    # then look at all the samples we have, and just print the fraction
    # of them that have X set to either '+' or '-'.
    total = float(N['+'] + N['-'])
    if total <= .5:
        print('No values...')
        return None
    QX = {'+': N['+']/total, '-': N['-']/total}
    return [QX, N]


#print(rejectionSample('Demoralize',bn,{'LeakIdea':'+','Infiltration':'+','NightDefense':'+','LeakIdea':'+'},10000,varss))
'''