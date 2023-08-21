from datetime import datetime
import json
import random
import csv
import copy
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

from initialization import createMemory,createVariables,printInitialization,\
                                    memoryLatex,fill_memory,create_char_memory

from feedback import createFeedback
from ex_creation import max_pattern_by_category,selection,PatternsCreation,pattern_choice_tot
from parameters import *

OUPUT_EXERCISES = "exercises"
OUPUT_SOLUTIONS = "solutions"
OUPUT_FEEDBACK = "feedbacks"

"""
Check if the memory parameters are compatible with the correct behaviour of the Program
Print the explanation of the problem and exit
"""
def check_memory_param():
    if MAX_MEMORY_INTERVAL[1]-MAX_MEMORY_INTERVAL[0] <= MEMORY_RANGE:
        print("To small MAX_MEMORY_INTERVAL for the MEMORY_RANGE")
        exit()
    if NBR_VISIBLE_ADDRESS*4 > MEMORY_RANGE:
        print("The memory range is too small for the number of visible addresses")
        exit()
    if MAX_NBR_MEMORY_BLOCKS < 2:
        print("MAX_NBR_MEMORY_BLOCKS needs to be greater or equal to 2")
        exit()


"""
Check if the choosen variable repartition is compatible with the correct behaviour of the Program
Take as input the variable repartion : [nbr of simple, nbr of pointer, nbr of array, nbr of char]
Print the explanation of the problem and return -1
"""
def check_variable_repartition(var_repartition):
    if var_repartition[0] < 2:
        print("The minimum number of simple variables must be greater than or equal to 2.")
        return -1
    if var_repartition[1]+var_repartition[2] < 1:
        print("You must use at least one pointer or array.")
        return -1
    if var_repartition[0] < var_repartition[1]:
        print("The number of pointer exceeds the number of simple variables.")
        return -1

    return 0


"""
Generate "nbr" of exercises
Input : the number of exercises
Output : exercises in latex file in the folder exercises,
         solution in txt file in the folder solutions,
         feedback in json file in the folder feedbacks
"""
def create_exercises(nbr):

    check_memory_param()

    nbr_ex_not_generated = 0


    #select exercise repartition if the repartition is forced (with FORCED_EXERCISE_REPARTITIONS)
    #select exercise and variable repartition if parameters SIMILAR_EXERCISES is true
    if FORCED_EXERCISE_REPARTITIONS:
        ex_repartition = FORCED_EXERCISE_REPARTITIONS
    elif SIMILAR_EXERCISES :
        ex_repartition = random.choice(EXERCISE_REPARTITIONS)
        var_repartition = random.choice(VARIABLE_REPARTITIONS)
        #select nbr of char variable if ex_repartition contains char category
        if sum(ex_repartition[5]) > 0:
            var_repartition.append(random.choice(VARIABLE_CHAR_REPARTITIONS))
        else:
            var_repartition.append(0)


    PatternsCreation()

    #variable used to observed the difference between expressions from the same pattern
    max_pattern = max_pattern_by_category()
    total_vector = [[[]for _ in range(max_pattern[i])] for i in range(7)]

    #create all exercises individually
    for n in range(nbr):

        #select exercise and variable if it was not done previously
        if FORCED_EXERCISE_REPARTITIONS or not SIMILAR_EXERCISES :
            if not FORCED_EXERCISE_REPARTITIONS:
                ex_repartition = random.choice(EXERCISE_REPARTITIONS)
            var_repartition = random.choice(VARIABLE_REPARTITIONS)
            #select nbr of char variable if ex_repartition contains char category
            if sum(ex_repartition[5]) > 0:
                var_repartition.append(random.choice(VARIABLE_CHAR_REPARTITIONS))
            else:
                var_repartition.append(0)


        if check_variable_repartition(var_repartition):
            nbr_ex_not_generated +=1
            continue


        variables = createVariables(var_repartition)

        memory = createMemory(variables)
        #if the memory could not be generated due to char
        if not memory:
            nbr_ex_not_generated +=1
            continue
        ex  = selection(memory, variables,ex_repartition)
        #if all categories could not select its number of expression
        if not ex:
            nbr_ex_not_generated +=1
            continue


        #Output Creation

        exercises = ""
        solution = ""
        sol = {}
        ex_before_char = 0
        v_i = 0
        ex_type = 0

        #number of expressions before char expressions because they need particular memory
        char_memory = create_char_memory(variables)
        for i in range(5):
            ex_before_char += sum(ex_repartition[i])
        #for each each expressions compute

        #           solution,feedback,result_vector(for total_vector)
        for i in range(len(ex)):

            exercises +="\item \\texttt{" + ex[i].latex() +"}\n"

            if i < ex_before_char or i >= ex_before_char + sum(ex_repartition[5]):
                _,_,_, result = ex[i].solution(memory)
            else:#case of char expression
                _,_,_, result = ex[i].solution(char_memory)

            solution += str(i) + " : " + ex[i].printExpr() + " : " + str(result)+"\n"

            if i < ex_before_char or i >= ex_before_char + sum(ex_repartition[5]):
                sol[i] = createFeedback(ex[i],memory)
                vector = ex[i].result_vector(memory)
            else:#case of char expression
                sol[i] = createFeedback(ex[i],char_memory)
                vector = ex[i].result_vector(char_memory)

            #class the expressions according to its category and its pattern
            total_vector[ex_type][pattern_choice_tot[n-nbr_ex_not_generated][ex_type][v_i]-1].append(vector)
            v_i+=1
            while ex_type < len(pattern_choice_tot[n-nbr_ex_not_generated]) and \
                            len(pattern_choice_tot[n-nbr_ex_not_generated][ex_type]) <= v_i:
                v_i = 0
                ex_type +=1

        #Write output in the corresponding files and folder

        fill_template = {}
        fill_template["declaration"] = printInitialization(variables,memory)
        fill_template["minMemory"] = min(memory)
        fill_template["maxMemory"] = max(memory)
        fill_template["exercises"] = exercises
        fill_template["memory"] = memoryLatex(memory, variables)

        if MERGE_OUTPUT:#single latex for all exercises
            template = open('templates/one_ex_template.tex', 'r').read()
            page = template%fill_template
            if n == 0:
                template = open('templates/glabal_template.tex', 'r').read()
                open(OUPUT_EXERCISES+"/result.tex", 'w').write(template)
                open(OUPUT_EXERCISES+"/result.tex", 'a').write(page)
            else:
                open(OUPUT_EXERCISES+"/result.tex", 'a').write(page)

        else:#single latex per exercise
            template = open('templates/one_by_one_template.tex', 'r').read()
            page = template%fill_template
            open(OUPUT_EXERCISES+"/result"+str(n)+".tex", 'w').write(page)

        open(OUPUT_FEEDBACK+"/feedback"+ str(n) +".json", 'w').write(json.dumps(sol,indent = 2))

        open(OUPUT_SOLUTIONS+"/solution"+ str(n) +".txt", 'w').write(solution)

    if MERGE_OUTPUT:
        open(OUPUT_EXERCISES+"/result.tex", 'a').write("\end{document}")


    if ANALYSES:
        analyse(total_vector)


    output_text = ""
    output_text += "The exercises can be found in the folder " + OUPUT_EXERCISES + ".\n"
    output_text += "The solutions can be found in the folder " + OUPUT_SOLUTIONS + ".\n"
    output_text += "The feedback can be found in the folder " + OUPUT_FEEDBACK + "."

    if nbr_ex_not_generated == 0:
        print("All the exercises have been generated.\n"+output_text)
    else:
        if nbr_ex_not_generated == nbr:
            print(str(nbr_ex_not_generated) +" of the "+str(nbr)+ " exercises could not be generated.")
        else:
            print(str(nbr_ex_not_generated) +" of the "+str(nbr)+ " exercises could not be generated.\n"+output_text)




"""
Perform the analyses of the behaviour of the program
Input : total_vector, contains the
Output : distribution and dot cloud graphs in the folder graphs,
         csv file containing all the ratio bewteen the number of different expression divided
                    by the number of time the pattern is used (made for each pattern)
"""
def analyse(total_vector):
    tot_distribution = []
    max_pattern = max_pattern_by_category()

    #Create distribution and cloud graph for each expression category
    for ex_type in range(len(pattern_choice_tot[0])):

        #cloud graph
        plt.figure()
        for ex_num in range(len(pattern_choice_tot)):
            x = pattern_choice_tot[ex_num][ex_type]
            y = [ex_num for _ in range(len(pattern_choice_tot[ex_num][ex_type]))]

            plt.scatter(x,y, color ="blue")
        plt.xlabel('Pattern number')
        plt.ylabel('Exercice number')
        plt.xticks(np.arange(0, max_pattern[ex_type]+1, 1))
        plt.savefig("graphs/nuage"+str(ex_type)+".png")

        #distribution graph
        distribution = []
        for ex_num in range(len(pattern_choice_tot)):
            for y in pattern_choice_tot[ex_num][ex_type]:
                try:
                    distribution[y-1] += 1
                except IndexError:
                    for _ in range(y-len(distribution)):
                        distribution.append(0)
                    distribution[y-1] += 1

        tot_distribution.append(distribution)
        distribution = distribution/np.sum(distribution)

        x = [ex_num+1 for ex_num in range(len(distribution))]
        plt.figure()
        plt.bar(x,distribution)
        plt.xticks(np.arange(0, max_pattern[ex_type]+1, 1))
        plt.xlabel('Pattern number')
        plt.ylabel('Percentage')
        plt.savefig("graphs/distribution"+str(ex_type)+".png")

    #Analyse if the expressions for one pattern need a different reasoning
    #return for each pattern the number of different reasoning for exprssions
    #generated from the same pattern divided by the number of time this pattern
    #is used

    #If set_up_csv true generate the csv file with 3 columns (category number,
    #                                            pattern number and result)
    #If set_up_csv false add just one column to the existing csv file
    set_up_csv = True
    if set_up_csv:
        with open('csv/vector.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Ex_num", "value"])
            for i in range(len(total_vector)):
                for y in range(len(total_vector[i])):
                    if total_vector[i][y] :
                        if tot_distribution[i][y] == 0:#pattern not used
                            writer.writerow([i, y+1, 0])
                        else:
                            #len(set(map(vector))) for the number of different reasoning
                            #divided by the occurance of the pattern
                            writer.writerow([i, y+1, round(len(set( \
                                    map(tuple, total_vector[i][y])))/tot_distribution[i][y],2)])
                    else:
                        writer.writerow([i, y+1, 0])
    else:
        col= []
        for i in range(len(total_vector)):
            for y in range(len(total_vector[i])):
                if total_vector[i][y] :
                    if tot_distribution[i][y] == 0:
                        col.append(0)
                    else:
                        col.append(round(len(set( \
                                    map(tuple, total_vector[i][y])))/tot_distribution[i][y],2))
                else:
                    col.append(0)

        csv_file = pd.read_csv('csv/vector.csv')
        csv_file['new2'] = col
        csv_file.to_csv('csv/vector.csv')


"""
Genereate "NBR_EXERCISES" differents exercises
"""
if __name__ == "__main__":
    random.seed(datetime.now().timestamp())
    create_exercises(NBR_EXERCISES)
