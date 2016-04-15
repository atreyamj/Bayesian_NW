DECISION_VAR_LIST=[]

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


  #  print queries
    print bayes_network
   # print all_vars
  #  print utility
    return queries, bayes_network, utility, all_vars

read_file_data(open('C:\Users\Atreya\PycharmProjects\Bayesian_NW\HW3_samples_updated\HW3_samples\sample01.txt'))