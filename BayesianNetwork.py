from decimal import Decimal
import copy
import itertools


class ReadFromFile:
    bayeNW = {}
    Query_List = []
    TopoSortedVars = []

    # filename = sys.argv[-1]

    def SortVars(self, networkDictionary):
        var = networkDictionary.keys()
        l = []
        while len(l) < len(var):
            for v in var:
                if v not in l and all(x in l for x in networkDictionary[v]['Parents']):
                    l.append(v)
        return l

    def getSeparatorCount(self, fileString):
        return fileString.count('|')

    def addParenttoNetwork(self, Child, Parentlist):
        self.bayeNW[Child.strip('\n')]['Parents'] = Parentlist
        return

    def addChildrentoNetwork(self, Parent, Children):
        self.bayeNW[Parent.strip('\n')]['Children'] = Children
        return

    def addCondProbtoNetwork(self, Var, CondProbValues):
        self.bayeNW[Var.strip('\n')]['Conditional_Prob'] = CondProbValues
        return

    def addProbtoNetwork(self, Var, ProbValues):
        self.bayeNW[Var.strip('\n')]['Probability'] = ProbValues
        return

    def addVarTypetoNetwork(self, Var, TypeValue):
        self.bayeNW[Var.strip('\n')]['Type'] = TypeValue
        return

    def getBayesNetwork(self):
        return self.bayeNW

    def getQueriesforNetwork(self):
        return self.Query_List

    def getSortedVars(self):
        return self.TopoSortedVars

    def ParseFile(self, FileName):
        FileHandler = open(FileName)
        currLine = FileHandler.readline().strip()
        i = 0
        while currLine[0] != '*':
            self.Query_List.append(currLine)
            currLine = FileHandler.readline().strip()

        currentLine = FileHandler.readline().strip()
        while currentLine != '':
            prevLine = currentLine
            Separator_Count = self.getSeparatorCount(prevLine)
            if Separator_Count == 0:
                var_decision = FileHandler.readline().strip()
                if var_decision[0] == 'd':

                    self.bayeNW[prevLine.strip('\n')] = {'Parents': [], 'Probability': var_decision.strip('\n'),
                                                         'Conditional_Prob': [], 'Type': 'Decision'}
                    self.addChildrentoNetwork(prevLine, [])
                else:
                    self.bayeNW[prevLine.strip('\n')] = {'Parents': [], 'Probability': var_decision.strip('\n'),
                                                         'Conditional_Prob': [], 'Type': 'Normal'}
                    self.addChildrentoNetwork(prevLine, [])

            else:
                prevLine_Split = prevLine.split(' | ')
                parents_Line = prevLine_Split[1].split(' ')
                for i in range(0, len(parents_Line)):
                    self.bayeNW[parents_Line[i]]['Children'].append(prevLine_Split[0].strip())

                self.bayeNW[prevLine_Split[0].strip('\n')] = {}
                self.addParenttoNetwork(prevLine_Split[0], parents_Line)
                self.addChildrentoNetwork(prevLine_Split[0], [])
                scenario_prob = {}
                for i in range(0, pow(2, len(parents_Line))):
                    cond_prob = FileHandler.readline().strip()
                    split_Cond_Prob = cond_prob.split(' ')
                    prob = split_Cond_Prob[0]
                    truthLine = split_Cond_Prob[1:]
                    truth = tuple(True if x == '+' else False for x in truthLine)
                    scenario_prob[truth] = prob

                self.addCondProbtoNetwork(prevLine_Split[0], scenario_prob)
                self.addProbtoNetwork(prevLine_Split[0], [])
                self.addVarTypetoNetwork(prevLine_Split[0], 'Normal')
            currentLine = FileHandler.readline()
            currentLine = FileHandler.readline().strip()
        TopoSortedVars = self.SortVars(self.bayeNW)
        return TopoSortedVars


class BayesianNetwork:
    InputParser = ReadFromFile()
    BayesNet = {}
    QueriesList = []
    SortedVars = []

    def InitNetwork(self,fileName):
        self.SortedVars=self.InputParser.ParseFile(fileName)
        self.BayesNet = self.InputParser.getBayesNetwork()
        self.QueriesList = self.InputParser.getQueriesforNetwork()
        # = self.InputParser.getSortedVars()

    def getSelectedNodes(self, sortedVariables, networkDictionary, observedVariables):
        x = observedVariables.keys()
        newNetwork = []

        bnPresence = [True if a in x else False for a in sortedVariables]

        for i in range(0, pow(len(sortedVariables), 2)):
            for v in sortedVariables:
                if bnPresence[sortedVariables.index(v)] != True and any(
                                bnPresence[sortedVariables.index(c)] == True for c in networkDictionary[v]['Children']):
                    index = sortedVariables.index(v)
                    bnPresence[index] = True

        for eachNode in sortedVariables:
            if bnPresence[sortedVariables.index(eachNode)] == True:
                newNetwork.append(eachNode)

        return newNetwork

    def getProbabilityQueryType(self, query):
        return query[0]

    def getProbability_var(self, Y, e):

        if self.BayesNet[Y]['Type'] == 'Decision':
            return 1.0

        if len(self.BayesNet[Y]['Parents']) == 0:
            if e[Y] == True:
                prob = float(self.BayesNet[Y]['Probability'])
                return float(self.BayesNet[Y]['Probability'])
            else:
                return 1.0-float(self.BayesNet[Y]['Probability'])
        else:

            parents = tuple(e[p] for p in self.BayesNet[Y]['Parents'])

            # query for prob of Y = y
            if e[Y] == True:
                return float(self.BayesNet[Y]['Conditional_Prob'][parents])
            else:
                return 1.0-float(self.BayesNet[Y]['Conditional_Prob'][parents])

    def enumerateAll(self,X, vars, e):
        if not vars:
            return 1.0
        Y = vars[0]
        if Y in e:
            returnValue = self.getProbability_var(Y, e) * self.enumerateAll(X, vars[1:], e)
        else:
            prob = []
            e2 = copy.deepcopy(e)
            for eachValue in [True, False]:
                e2[Y] = eachValue
                prob.append(self.getProbability_var(Y, e2) * self.enumerateAll(X,vars[1:], e2))
            returnValue = sum(prob)
        return returnValue

    def enumerateAsk(self):
        for i in range(0, len(self.QueriesList)):
            givenquery = self.QueriesList[i]
            if self.getProbabilityQueryType(givenquery) == 'P':
                splitgivenquery = givenquery.split('(')
                # queryfunction = splitgivenquery[0]
                query_values = splitgivenquery[1]
                query_vars = 0
                Dictionary = {}
                evident_Dictionary = {}
                variables = []
                var_boolvalues = []
                X = ''
                flag = False

                if query_values.count('|') == 1:
                    flag = True
                    b = query_values[:query_values.index('|')]
                    if b.find(",") != -1:
                        b_split = b.split(", ")
                        for i in range(0, len(b_split)):
                            query_vars = query_vars + 1
                            b_split_rest = b_split[i][:b_split[i].index(' ')]
                            variables.append(b_split_rest)
                            if b_split[i].find('+') != -1:
                                var_boolvalues.append(True)
                            else:
                                var_boolvalues.append((False))
                    else:
                        query_vars = 1
                        X = b[:b.index(' ')]
                        variables.append(X)
                        if b.find('+') != -1:
                            var_boolvalues.append(True)
                        else:
                            var_boolvalues.append(False)
                    d = query_values[query_values.index('| ') + 2:]
                else:
                    d = query_values
                e = d.split(', ')

                for i in range(0, len(e)):
                    variables.append((e[i][:e[i].index(' =')]))
                    if e[i].find('+') != -1:
                        var_boolvalues.append(True)
                    else:
                        var_boolvalues.append(False)
                for i in range(0, len(variables)):
                    Dictionary[variables[i]] = var_boolvalues[i]

                bn = self.getSelectedNodes(self.SortedVars, self.BayesNet,
                                           Dictionary)  # now create a network of only those nodes that we need to calculate the given query
                Prob = self.enumerateAll(X, bn, Dictionary)

                # If the query is of the form P(X|e) i.e. flag is true, we have to divide "calculatedProbability" it by P(e).
                # So now we create all the terms and network needed to calculate just P(e) and then perform the division

                if flag == True:
                    X2 = ''
                    evidenceValue = var_boolvalues[query_vars:]
                    evidenceVariables = variables[query_vars:]
                    for i in range(0, len(evidenceVariables)):
                        evident_Dictionary[evidenceVariables[i]] = evidenceValue[i]
                    evidenceBN = self.getSelectedNodes(self.SortedVars, self.BayesNet, Dictionary)
                    quotient = self.enumerateAll(X2, evidenceBN, evident_Dictionary)
                    probResult = Decimal(str(Prob / quotient)).quantize(
                        Decimal('.01'))  # Rounding off to 2 decimal places
                    print(probResult)
                else:
                    probResult = Decimal(str(Prob)).quantize(Decimal('.01'))  # Rounding off to 2 decimal places
                    print(probResult)

            elif self.getProbabilityQueryType(givenquery) == 'E':
                splitgivenquery = givenquery.split('(')
                # queryfunction = splitgivenquery[0]                    #It can be 'P', 'EU' or 'MEU'
                query_values = splitgivenquery[1]  # The part of the query after the opening bracket
                query_vars = 0
                Dictionary = {}
                evident_Dictionary = {}
                variables = []
                var_boolvalues = []
                X = ''
                flag = False
                variables.append('utility')
                var_boolvalues.append(True)
                if query_values.count('|') == 1:  # Extract the query variable appearing before the '|'
                    flag = True
                    b = query_values[:query_values.index('|')]
                    if b.find(",") != -1:
                        b_split = b.split(", ")
                        for i in range(0, len(b_split)):
                            query_vars = query_vars + 1
                            b_split_rest = b_split[i][:b_split[i].index(' ')]
                            variables.append(b_split_rest)
                            if b_split[i].find('+') != -1:
                                var_boolvalues.append(True)
                            else:
                                var_boolvalues.append((False))
                    else:
                        query_vars = 1
                        X = b[:b.index(' ')]
                        variables.append(X)  # Query variable. eg. P(X|e)
                        if b.find('+') != -1:
                            var_boolvalues.append(True)
                        else:
                            var_boolvalues.append(False)
                    d = query_values[query_values.index('| ') + 2:]  # 'd' will store the part after the '|'
                else:  # If '|' is not present in the given query
                    d = query_values  # In this case, 'd' will be the entire query itself
                e = d.split(', ')
                for i in range(0, len(e)):  # Check for each variable whose value is already given in the query
                    variables.append((e[i][:e[i].index(' =')]))
                    if e[i].find('+') != -1:
                        var_boolvalues.append(True)
                    else:
                        var_boolvalues.append(False)
                for i in range(0, len(variables)):
                    Dictionary[variables[i]] = var_boolvalues[i]
                bn = self.getSelectedNodes(self.SortedVars, self.BayesNet,
                                           Dictionary)  # now create a network of only those nodes that we need to calculate the given query

                Prob = self.enumerateAll(X, bn, Dictionary)

                # If the query is of the form P(X|e) i.e. flag is true, we have to divide "calculatedProbability" it by P(e).
                # So now we create all the terms and network needed to calculate just P(e) and then perform the division

                if flag == True:
                    X2 = ''
                    evidenceVariables = variables[query_vars:]
                    evidenceValue = var_boolvalues[query_vars:]
                    for i in range(0, len(evidenceVariables)):
                        evident_Dictionary[evidenceVariables[i]] = evidenceValue[i]
                    evidenceBN = self.getSelectedNodes(self.SortedVars, self.BayesNet, evident_Dictionary)
                    quotient = self.enumerateAll(X2, evidenceBN, evident_Dictionary)
                    probResult = Decimal(str(Prob / quotient)).quantize(
                        Decimal('.01'))  # Rounding off to 2 decimal places
                    print(int(round(probResult)))
                else:
                    probResult = Decimal(str(Prob)).quantize(Decimal('.01'))  # Rounding off to 2 decimal places
                    print(int(round(probResult)))

            elif self.getProbabilityQueryType(givenquery) == 'M':
                splitgivenquery = givenquery.split('(')
                queryfunction = splitgivenquery[0]  # It can be 'P', 'EU' or 'MEU'
                # print(function)

                query_values = splitgivenquery[1]  # The part of the query after the opening bracket

                MEU_vars = []
                query_vars = 0
                Dictionary = {}
                evident_Dictionary = {}
                variables = []
                var_boolvalues = []
                X = ''
                flag = False
                resultDictionary = {}
                variables.append('utility')
                var_boolvalues.append(True)
                if query_values.count('|') == 1:  # Extract the query variable appearing before the '|'
                    flag = True
                    b = query_values[:query_values.index('|')]
                    if b.find(",") != -1:
                        b_split = b.split(", ")
                        for i in range(0, len(b_split)):
                            if b_split[i].find('=')!=0:
                                query_vars = query_vars + 1
                                variables.append(b_split[i][:b_split[i].index(' ')])
                                if b_split[i].find('+') != -1:
                                    var_boolvalues.append(True)
                                else:
                                    var_boolvalues.append((False))
                            else:
                                MEU_vars.append(b_split[i][:b_split[i].index(' ')])
                                # print(variables)
                                # print(queryVariables)

                    else:

                        query_vars = 1
                        X = b[:b.index(' ')]
                        if b.find('=') != -1:
                            variables.append(X)  # Query variable. eg. P(X|e)
                            if b.find('+') != -1:
                                var_boolvalues.append(True)
                            else:
                                var_boolvalues.append(False)
                        else:
                            MEU_vars.append(X)

                    d = query_values[query_values.index('| ') + 2:]  # 'd' will store the part after the '|'


                else:  # If '|' is not present in the given query
                    d = query_values  # In this case, 'd' will be the entire query itself

                e = d.split(', ')

                for i in range(0, len(e)):  # Check for each variable whose value is already given in the query
                    if e[i].find('=') != -1:
                        variables.append((e[i][:e[i].index(' =')]))
                        if e[i].find('+') != -1:
                            var_boolvalues.append(True)
                        else:
                            var_boolvalues.append(False)
                    else:
                        MEU_vars.append(e[i].strip(")"))

                for i in range(0, len(variables)):
                    Dictionary[variables[i]] = var_boolvalues[i]

                MEU_Length = len(MEU_vars)

                MEU_TruthValue = list(itertools.product([True, False], repeat=MEU_Length))

                for i in range(0, len(MEU_TruthValue)):
                    tempEvidence = copy.deepcopy(Dictionary)
                    meuValue = ''
                    j = 0
                    for each in MEU_vars:
                        tempEvidence[each] = MEU_TruthValue[i][j]
                        if MEU_TruthValue[i][j] == True:
                            meuValue = meuValue + '+ '
                        else:
                            meuValue = meuValue + '- '
                        j = j + 1

                    bn = self.getSelectedNodes(self.SortedVars, self.BayesNet,
                                               tempEvidence)  # now create a network of only those nodes that we need to calculate the given query

                    Prob = self.enumerateAll(X, bn, tempEvidence)

                    if flag == True:
                        X2 = ''
                        evidenceVariables = variables[query_vars:]
                        evidenceValue = var_boolvalues[query_vars:]
                        for i in range(0, len(evidenceVariables)):
                            evident_Dictionary[evidenceVariables[i]] = evidenceValue[i]
                        evidenceBN = self.getSelectedNodes(self.SortedVars, self.BayesNet, evident_Dictionary)

                        quotient = self.enumerateAll(X2, evidenceBN, evident_Dictionary)

                        probResult = Decimal(str(Prob / quotient)).quantize(
                            Decimal('.01'))  # Rounding off to 2 decimal places
                        # print(int(round(finalResult)))


                    else:
                        probResult = Decimal(str(Prob)).quantize(Decimal('.01'))  # Rounding off to 2 decimal places
                        # print(int(round(finalResult)))

                    resultDictionary[probResult] = meuValue

                # print(resultDictionary)

                answer = max(resultDictionary.keys())

                print(resultDictionary[answer] + str(int(round(answer))))


BayeNetworkObj=BayesianNetwork()
BayeNetworkObj.InitNetwork("C:\Users\Atreya\PycharmProjects\Bayesian_NW\HW3_samples_updated\HW3_samples\sample04.txt")
BayeNetworkObj.enumerateAsk()