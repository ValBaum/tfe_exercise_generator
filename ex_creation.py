from parameters import *
from syntax import *
import copy

pattern_choice_tot = []
refuse_pattern = [[] for x in range(7)]


"""
Pattern Creation

create all possible pattern for the categories :
        - Easy
        - Incrementation and decrementation
        - pointer arithmetic
        - Cast
        - Array
        - Complex dereferencement

Using the class of the "syntax.py" file :
        - VariableExpr
        - Unop
        - Incr
        - Cast
        - Binop
        - Array
        - Function

"""

easy_ex = [[] for _ in range(5)]
def easy_pattern_creation():
    # simple_variable
    easy_ex[0].append((1,VariableExpr("simple_variable")))
    # pointer
    easy_ex[0].append((2,VariableExpr("pointer")))
    # array
    easy_ex[0].append((3,VariableExpr("array")))
    # &simple_variable
    easy_ex[0].append((4,Unop("&",VariableExpr("simple_variable"))))

    # *var
    easy_ex[1].append((5,Unop("*",VariableExpr())))
    # &*var
    easy_ex[1].append((6,Unop("&",Unop("*",VariableExpr()))))

    # **var
    easy_ex[2].append((7,Unop("*",Unop("*",VariableExpr()))))
    # &**var
    easy_ex[2].append((8,Unop("&",Unop("*",Unop("*",VariableExpr())))))

    # ***var
    easy_ex[3].append((9,Unop("*",Unop("*",Unop("*",VariableExpr())))))
    # &***var
    easy_ex[3].append((10,Unop("&",Unop("*",Unop("*",Unop("*",VariableExpr()))))))

    # ****var
    easy_ex[4].append((11,Unop("*",Unop("*",Unop("*",Unop("*",VariableExpr()))))))
    # &****var
    easy_ex[4].append((12,Unop("&",Unop("*",Unop("*",Unop("*",Unop("*",VariableExpr())))))))



incr_ex = []
def incr_pattern_creation():
    # *++--address
    incr_ex.append((1,Unop("*",Incr("left", VariableExpr("address"), "++--"))))
    # ++--*address
    incr_ex.append((2,Incr("left", Unop("*",VariableExpr("address")), "++--")))
    # ++--*&simple
    incr_ex.append((3,Incr("left", Unop("*", Unop("&", VariableExpr("simple_variable"))), "++--")))

    # *address++--
    incr_ex.append((4,Unop("*",Incr("right", VariableExpr("address"), "++--"))))
    # (*address)++--
    incr_ex.append((5,Incr("right", Unop("*", VariableExpr("address")), "++--")))
    # (*&simple)++--
    incr_ex.append((6,Incr("right", Unop("*", Unop("&", VariableExpr("simple_variable"))), "++--")))



arithmetic_ex = [[] for _ in range(2)]
def arithmetic_pattern_creation():
    # address +- value
    arithmetic_ex[0].append((1,Binop("+-",VariableExpr("address"),VariableExpr("value"))))
    # &simple +- value
    arithmetic_ex[0].append((2,Binop("+-",Unop("&",VariableExpr("simple_variable")),VariableExpr("value"))))
    # (int *) simple +- value
    arithmetic_ex[0].append((3,Binop("+-", Cast("int",1,VariableExpr("simple_variable")),VariableExpr("value"))))


    # address - address
    arithmetic_ex[0].append((4,Binop("-",VariableExpr("address"),VariableExpr("address"))))
    # address - &simple
    arithmetic_ex[0].append((5,Binop("-",VariableExpr("address"),Unop("&",VariableExpr("simple_variable")))))
    # &simple - address
    arithmetic_ex[0].append((6,Binop("-",Unop("&",VariableExpr("simple_variable")),VariableExpr("address"))))


    #simple +- value
    arithmetic_ex[0].append((7,Binop("+-",VariableExpr("simple_variable"),VariableExpr("value"))))
    #*&simple +- value
    arithmetic_ex[0].append((8,Binop("+-",Unop("*",Unop("&",VariableExpr("simple_variable"))),VariableExpr("value"))))


    # [++--]simple[++--] +- [++--]simple[++--]
    arithmetic_ex[1].append((9,Binop("+-",Incr("left_right",VariableExpr("simple_variable"),"++--"),Incr("left_right",VariableExpr("simple_variable"),"++--"))))
    # [++--]address[++--] +- [++--]simple[++--]
    arithmetic_ex[1].append((10,Binop("+-",Incr("left_right",VariableExpr("address"),"++--"),Incr("left_right",VariableExpr("simple_variable"),"++--"))))
    # [++--]address[++--] - [++--]addres[++--]
    arithmetic_ex[1].append((11,Binop("-",Incr("left_right",VariableExpr("address"),"++--"),Incr("left_right",VariableExpr("address"),"++--"))))
    #[++--]address[++--] + *(&simple_variable +- value)
    arithmetic_ex[1].append((12,Binop("+-",VariableExpr("address"),Unop("*",Binop("+-",Unop("&",VariableExpr("simple_variable")),VariableExpr("value"))))))
    # (int *)address + address[value]
    arithmetic_ex[1].append((13,Binop("+-", Cast("int",1,VariableExpr("simple_variable")),Array(VariableExpr("address"),VariableExpr("value")))))



cast_ex = []
def cast_pattern_creation():
    # (long/short *) address +- value
    cast_ex.append((1,Binop("+-", Cast("long_short",1,VariableExpr("address")),VariableExpr("value"))))
    # (long/short ) simple +- value
    cast_ex.append((2,Binop("+-", Cast("long_short",0,VariableExpr("simple_variable")),VariableExpr("value"))))
    # (long/short *) &simple +- value
    cast_ex.append((3,Binop("+-", Cast("long_short",1,Unop("&",VariableExpr("simple_variable"))),VariableExpr("value"))))
    # (long/short *) (address +- value)
    cast_ex.append((4, Cast("long_short",1, Binop("+-",VariableExpr("address"),VariableExpr("value")))))



array_ex = []
def array_pattern_creation():
    # address[value]
    array_ex.append((1,Array(VariableExpr("address"),VariableExpr("value"))))
    # address[- simple_var]
    array_ex.append((2,Array(VariableExpr("address"),Unop("-",VariableExpr("simple_variable")))))
    # address[value] +- address[value]
    array_ex.append((3,Binop("+-",Array(VariableExpr("address"),VariableExpr("value")),Array(VariableExpr("address"),VariableExpr("value")))))
    # address[value +- value]
    array_ex.append((4,Array(VariableExpr("address"),Binop("+-",VariableExpr("value"),VariableExpr("value")))))
    # address[tab[value] +- address[value]]
    array_ex.append((5,Array(VariableExpr("address"),Binop("+-",Array(VariableExpr("address"),VariableExpr("value")),Array(VariableExpr("address"),VariableExpr("value"))))))
    # address[address[value] +- value]
    array_ex.append((6,Array(VariableExpr("address"),Binop("+-",Array(VariableExpr("address"),VariableExpr("value")),VariableExpr("value")))))
    # (int* simple_var)[value]
    array_ex.append((7,Array(Cast("int", 1, VariableExpr("simple_variable")),VariableExpr("value"))))



char_ex = []
def char_pattern_creation():
    #char - char
    char_ex.append((1,Binop("-",VariableExpr("char"),VariableExpr("char"))))
    # *char
    char_ex.append((2,Unop("*",VariableExpr("char"))))
    #char[value] - char[value]
    char_ex.append((3,Binop("-",Array(VariableExpr("char"),VariableExpr("value")),Array(VariableExpr("char"),VariableExpr("value")))))
    #printf ("%s", c)
    char_ex.append((4,Function("printf",VariableExpr("char"))))
    #c [ c [ value ] - c [ value ]]
    char_ex.append((5,Array(VariableExpr("char"),Binop("-",Array(VariableExpr("char"),VariableExpr("value")),Array(VariableExpr("char"),VariableExpr("value"))))))



defer_ex = []
def defer_pattern_creation():
    #*(data = data2 )
    defer_ex.append((1,Binop("=",VariableExpr("address"),VariableExpr("address"))))

    l = 1 #number of other defer pattern
    for x in copy.copy(array_ex):
        l +=1
        defer_ex.append((l, x[1]))

    for x in copy.copy(arithmetic_ex[0]):
        l +=1
        defer_ex.append((l, x[1]))

    for x in copy.copy(arithmetic_ex[1]):
        l +=1
        defer_ex.append((l, x[1]))


"""
Generate all the pattern by calling the previous classes
"""
def PatternsCreation():
    easy_pattern_creation()
    incr_pattern_creation()
    arithmetic_pattern_creation()
    cast_pattern_creation()
    array_pattern_creation()
    char_pattern_creation()
    defer_pattern_creation()


"""
Generate the expressions from the pattern. It select a pattern according to the expression
category repartition and from it try to generate the expression.
Input : memory(dict), variables(List), repartion (list of list)
Output : a list of selected expressions
"""
def selection(memory, variables, repartition):
    ex = []
    pattern_choice_ex = []

    #copy the different pattern to avoid interference bewteen exercises
    copy_easy_ex = []
    copy_arithmetic_ex = []
    for i in range(len(easy_ex)):
        copy_easy_ex.append(copy.copy(easy_ex[i]))
    for i in range(len(arithmetic_ex)):
        copy_arithmetic_ex.append(copy.copy(arithmetic_ex[i]))
    copy_array_ex = copy.copy(array_ex)
    copy_incr_ex = copy.copy(incr_ex)
    copy_cast_ex = copy.copy(cast_ex)
    copy_char_ex = copy.copy(char_ex)
    copy_defer_ex = copy.copy(defer_ex)

    #Easy exercises

    pattern_choice = []
    for i in range(len(repartition[0])):
        for nbr in range(repartition[0][i]):
            if not copy_easy_ex[i]: #if no pattern left for selection
                print("Fail to generate an exercise : in selection too many easy "+str(i)+" in repartition parameters (give "+str(repartition[0][i])+")")
                return []
            e = random.choice(copy_easy_ex[i])
            copy_easy_ex[i].remove(e)

            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(memory, copy.copy(variables)):
                refuse_pattern[0].append(copy_e[0])
                if not copy_easy_ex[i]:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many easy "+str(i)+" in repartition parameters (give "+str(repartition[0][i])+")")
                    return []
                e = random.choice(copy_easy_ex[i])
                copy_easy_ex[i].remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)


    #Incrementation and decrementation
    pattern_choice = []
    #le nombre max peut etre 5 et non 6 si la variable est isolée et donc *++--var n'est pas possible
    for i in range(len(repartition[1])):
        for nbr in range(repartition[1][i]):
            if not copy_incr_ex:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Incr in repartition parameters (give "+str(repartition[1][i])+")")
                return []
            e = random.choice(copy_incr_ex)
            copy_incr_ex.remove(e)
            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(memory, copy.copy(variables)):
                refuse_pattern[1].append(copy_e[0])
                if not copy_incr_ex:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Incr in repartition parameters (give "+str(repartition[1][i])+")")
                    return []
                e = random.choice(copy_incr_ex)
                copy_incr_ex.remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])

    pattern_choice_ex.append(pattern_choice)


    #Pointer arithmetic
    pattern_choice = []
    for i in range(len(repartition[2])):
        for nbr in range(repartition[2][i]):
            if not copy_arithmetic_ex[i]:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Arith "+str(i)+" in repartition parameters (give "+str(repartition[2][i])+")")
                return []
            e = random.choice(copy_arithmetic_ex[i])
            copy_arithmetic_ex[i].remove(e)
            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(memory, copy.copy(variables)):
                refuse_pattern[2].append(copy_e[0])
                if not copy_arithmetic_ex[i]:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Arith "+str(i)+" in repartition parameters (give "+str(repartition[2][i])+")")
                    return []
                e = random.choice(copy_arithmetic_ex[i])
                copy_arithmetic_ex[i].remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)

    #Cast exercises
    pattern_choice = []
    for i in range(len(repartition[3])):
        for nbr in range(repartition[3][i]):
            if not copy_cast_ex:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Cast in repartition parameters (give "+str(repartition[3][i])+")")
                return []
            e = random.choice(copy_cast_ex)
            copy_cast_ex.remove(e)
            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(memory, copy.copy(variables)):
                refuse_pattern[3].append(copy_e[0])
                if not copy_cast_ex:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Cast in repartition parameters (give "+str(repartition[3][i])+")")
                    return []
                e = random.choice(copy_cast_ex)
                copy_cast_ex.remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)


    #Array exercises
    pattern_choice = []
    for i in range(len(repartition[4])):
        for nbr in range(repartition[4][i]):
            if not copy_array_ex:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Array in repartition parameters (give "+str(repartition[4][i])+")")
                return []
            e = random.choice(copy_array_ex)
            copy_array_ex.remove(e)
            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(memory, copy.copy(variables)):
                refuse_pattern[4].append(copy_e[0])
                if not copy_array_ex:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Array in repartition parameters (give "+str(repartition[4][i])+")")
                    return []
                e = random.choice(copy_array_ex)
                copy_array_ex.remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)



    #Char exercises


    #create the char array
    char_memory = create_char_memory(variables)

    #select only char variables and also assign addresses according to the char_memory
    char_variables = []
    for v1 in variables:
        if isinstance(v1, Char_variable):
            char_variables.append(v1)
            if v1.value == None:
                for v2 in char_variables:

                    if v2.name == v1.variable_reference:
                        v1.begin_address = v2.begin_address + v1.variable_shift


    pattern_choice = []
    for i in range(len(repartition[5])):
        for nbr in range(repartition[5][i]):
            if not copy_char_ex:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Char in repartition parameters (give "+str(repartition[5][i])+")")
                return []
            e = random.choice(copy_char_ex)
            copy_char_ex.remove(e)
            copy_e = copy.deepcopy(e)
            while not copy_e[1].selection(char_memory, copy.copy(char_variables)):
                refuse_pattern[5].append(copy_e[0])
                if not copy_char_ex:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Char in repartition parameters (give "+str(repartition[5][i])+")")
                    return []
                e = random.choice(copy_char_ex)
                copy_char_ex.remove(e)
                copy_e = copy.deepcopy(e)
            ex.append(copy_e[1])
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)



    #Complex deferencement

    pattern_choice = []
    for i in range(len(repartition[6])):
        for nbr in range(repartition[6][i]):
            if not copy_defer_ex:#if no pattern left for selection
                print("Fail to generate an exercise : in selection too many Defer in repartition parameters (give "+str(repartition[6][i])+")")
                return []
            e = random.choice(copy_defer_ex)
            copy_defer_ex.remove(e)
            copy_e = copy.deepcopy(e)
            test = Unop("*",copy_e[1])
            while not test.selection(memory, copy.copy(variables)):
                refuse_pattern[0].append(copy_e[0])
                if not copy_defer_ex:#if no pattern left for selection
                    print("Fail to generate an exercise : in selection too many Defer in repartition parameters (give "+str(repartition[6][i])+")")
                    return []
                e = random.choice(copy_defer_ex)
                copy_defer_ex.remove(e)
                copy_e = copy.deepcopy(e)
                test = Unop("*",copy_e[1])
            ex.append(test)
            pattern_choice.append(copy_e[0])
    pattern_choice_ex.append(pattern_choice)

    pattern_choice_tot.append(pattern_choice_ex)

    return ex


"""
Return a list with each element correspond to the number of pattern of its category
"""
def max_pattern_by_category():

    max_pattern = []
    max_pattern.append(sum([len(x) for x in easy_ex]))
    max_pattern.append(len(incr_ex))
    max_pattern.append(sum([len(x) for x in arithmetic_ex]))
    max_pattern.append(len(cast_ex))
    max_pattern.append(len(array_ex))
    max_pattern.append(len(char_ex))
    max_pattern.append(len(defer_ex))
    return max_pattern
