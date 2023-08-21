import random
import copy
import parameters
import numbers
from initialization import *

# Probability of making the error
error_probabilities = [0.5 for i in range(18)]
#maximum nbr of error for one feedback
max_error = 2

#conversion type to nbr of bytes
type_conversion = {
    "short" : 2,
    "int" : 4,
    "long" : 8,
    "char": 1
}



"""
Class responsible of feedbacks
The class is used once per feedback value
"""
class Feedback():
    def __init__(self, pointer_length, address_size, address, value, error_type, proba):
        self.pointer_length = pointer_length
        self.address_size = address_size
        self.address = address
        self.value = value
        self.error_type = error_type    #code number corresponding to an error
        self.proba = proba  #Probability making the error

    #return the current state of the feedback
    def values(self):
        return self.pointer_length, self.address_size, self.address, self.value

    #update the feedback values
    def changeValues(self, pointer_length, address_size, address, value, error_type = None):
        self.pointer_length = pointer_length
        self.address_size = address_size
        self.address = address
        self.value = value
        if error_type:
            self.error_type.append(error_type)

"""
Select all the possible variables given the pattern and the number of time the
value is dereferenced.
Input : pattern (string describing the wanted proprieties)
        variables (the list of variable)
        nbr_defer (the number of time the value is dereferenced)
Output : a list of possible values
"""
def selectVariables(pattern, variables ,nbr_defer):
    selectVariables = []
    if pattern == "simple_variable":
        for v in variables:
            if isinstance(v, Simple_variable) and nbr_defer <= v.MAX_CAST:
                selectVariables.append(v)
    elif pattern == "pointer":
        for v in variables:
            if isinstance(v, Pointer_variable):
                selectVariables.append(v)
    elif pattern == "array":
        for v in variables:
            if isinstance(v, Array_variable):
                selectVariables.append(v)
    elif pattern == "char":
        for v in variables:
            if isinstance(v, Char_variable):
                selectVariables.append(v)
    elif pattern == "address":
        for v in variables:
            if isinstance(v, Pointer_variable):
                selectVariables.append(v)
            elif isinstance(v, Array_variable):
                selectVariables.append(v)
    elif pattern == "value":
        for v in variables:
            if isinstance(v, Simple_variable):
                selectVariables.append(v)
    elif pattern == "all":
        for v in variables:
            if isinstance(v, Simple_variable) and v.MAX_CAST >= nbr_defer:
                selectVariables.append(v)
            elif isinstance(v, Pointer_variable) and v.MAX_CAST+1 >= nbr_defer:
                selectVariables.append(v)
            elif isinstance(v, Array_variable)  and 1 >= nbr_defer:
                selectVariables.append(v)

    return selectVariables

"""
Abstract syntax tree

Different classes :
    - VariableExpr : Represents the variables
    - Unop : Represents unary operations
    - Incr : Represents incrementation and decrementation
    - Binop : Represents binary operations
    - Cast : Represents casting operations
    - Array : Represents arrays (variable[index])
    - Function : Represents functions

Each classes implements the following functions :
    - __init__ : allows to create the pattern and some attributes are given
                to specify proprieties of the class

    - printExpr : generate the expressions in a string

    - latex :  generate the expressions in a string for latex

    - selection : generate the expressions from the pattern. Make different choices to
                create different expressions. Return true if the expressions is
                created and false otherwise.

    - solution : perform the operation to obtain the solution,
                return 4 arguments : the pointer length
                                     the size of the memory
                                     the address of the expression if it exist
                                     the value of the expression

    - feedback : create the different feedback. It returns a list of the Feedback class
                corresponding to the correct values and values obtain when some errors are made

    - get_pointer_length : return the pointer length of the expressions.
            can used before the selection process

    - result_vector : create a list of pair values (address, value) for all its child classes
            the return vector takes the form (childs addresses, childs values, current address, current value)

"""
class VariableExpr():

    def __init__(self,pattern="all"):
        self.pattern = pattern
        self.variable = None


    def printExpr(self,nbr_defer=0):
        if isinstance(self.variable,Number):
            return self.variable.printExpr(nbr_defer)
        else:
            return self.variable.name


    def latex(self, nbr_defer=0):
        if isinstance(self.variable,Number):
            return self.variable.latex(nbr_defer)
        else:
            return self.variable.name


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        self.variable = None
        #select the possible choices of variables
        possible_variables = selectVariables(self.pattern, variables, nbr_defer)
        if not possible_variables and self.pattern != "value":#values can be a number
            return False

        random.shuffle(possible_variables)

        #if possibilities values are given, it selects accordingly
        if possibilities is not None:
            for v in possible_variables:
                if isinstance(v,Pointer_variable):
                    if v.pointing_variable.address in possibilities:
                        self.variable = v
                        variables.remove(v)
                        break
                elif isinstance(v,Array_variable):
                    if v.begin_address in possibilities:
                        self.variable = v
                        variables.remove(v)
                        break
                elif isinstance(v,Simple_variable):
                    if memory[v.address] in possibilities:
                        self.variable = v
                        variables.remove(v)
                        break
                elif isinstance(v,Char_variable):
                    if v.begin_address in possibilities:
                        self.variable = v
                        variables.remove(v)
                        break
        elif possible_variables:#if no possibilities choose first element
            self.variable = possible_variables[0]
            variables.remove(possible_variables[0])

        if self.variable == None and self.pattern == "value":
            self.variable = Number()
            if not self.variable.selection(memory, variables, nbr_defer, possibilities):
                return False
        elif self.variable == None:
            variables[:] = [] #remove all elements
            return False

        return True


    def solution(self,memory):
        if isinstance(self.variable,Simple_variable):
            return 0, type_conversion[self.variable.type], self.variable.address,  memory[self.variable.address]
        elif isinstance(self.variable,Pointer_variable):
            return self.variable.pointer_length, type_conversion[self.variable.type], None, self.variable.pointing_variable.address
        elif isinstance(self.variable,Array_variable):
            return 1, type_conversion[self.variable.type], None, self.variable.begin_address
        elif isinstance(self.variable,Char_variable):
            return 1, type_conversion["char"], None, self.variable.begin_address
        elif isinstance(self.variable,Number):
            return self.variable.solution(memory)


    def feedback(self,memory):
        feed = []
        pointer_length, address_size, address, value = self.solution(memory)
        feed.append(Feedback(pointer_length, address_size, address, value, [],1))
        if isinstance(self.variable,Simple_variable):
            #return the address
            feed.append(Feedback(0, type_conversion[self.variable.type], None,  self.variable.address, [1],error_probabilities[1]))
        elif isinstance(self.variable,Pointer_variable):
            #return the pointing value
            feed.append(Feedback(0, type_conversion[self.variable.type], self.variable.pointing_variable.address, memory[self.variable.pointing_variable.address],[2],error_probabilities[2]))
        elif isinstance(self.variable,Array_variable):
            #return the pointing value
            feed.append(Feedback(0, type_conversion[self.variable.type], self.variable.begin_address, memory[self.variable.begin_address],[2],error_probabilities[2]))
        return feed


    def result_vector(self,memory):
        _,_,address, result = self.solution(memory)
        return [address,result]

    def get_pointer_length(self):
        if self.pattern == "simple_variable" or self.pattern == "value":
            return 0
        elif self.pattern == "pointer" or self.pattern == "array" or self.pattern == "address" or self.pattern == "char":
            return 1
        elif self.pattern == "all":
            return 0


class Number():

    def __init__(self):
        self.number = None


    def printExpr(self,nbr_defer=0):
        return str(self.number)


    def latex(self, nbr_defer=0):
        return str(self.number)


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        if possibilities is None:
            self.number = random.randrange(1,5,1)
        else:
            possibilities = [x for x in possibilities if x != 0]
            if possibilities:
                self.number = random.choice(possibilities)
                return True
            else:#possibilities is empty
                return False


    def solution(self,memory):
        return 0, 0, None,self.number



class Unop():

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
        self.iscast = False#is determined in selction
        self.nbr_cast = 0#same as iscast

    def printExpr(self,nbr_defer=0):
        if self.op == "&":
            return "&" + self.expr.printExpr(nbr_defer)
        elif self.op == "*":
            if isinstance(self.expr,Binop) or isinstance(self.expr, Array):
                expr_str = "("+self.expr.printExpr(nbr_defer+1)+")"
            else:
                expr_str = self.expr.printExpr(nbr_defer+1)
            if self.iscast:
                s = "* (int " + "*"*(nbr_defer+1) + ")"
                return s +expr_str
            else:
                s = "*" + expr_str
                return s
        elif self.op == "-":
            return "-" + self.expr.printExpr(nbr_defer)


    def latex(self, nbr_defer=0):
        if self.op == "&":
            return "\\&" + self.expr.latex(nbr_defer)
        elif self.op == "*":
            if isinstance(self.expr,Binop) or isinstance(self.expr, Array):
                expr_str = "("+self.expr.latex(nbr_defer+1)+")"
            else:
                expr_str = self.expr.latex(nbr_defer+1)
            if self.iscast:
                s = "* (int " + "*"*(nbr_defer+1) + ")"
                return s +expr_str
            else:
                s = "*" + expr_str
                return s
        elif self.op == "-":
            return "-" + self.expr.latex(nbr_defer)


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):

        new_possibilities = None
        if self.op == "*":
            new_possibilities = []
            nbr_defer += 1
            #dereference needs a memory address
            for x in memory.keys():
                if not possibilities or memory[x] in possibilities:
                    new_possibilities.append(x)
            if not new_possibilities:
                return False
        elif self.op == "&" and nbr_defer > 0:
            nbr_defer -= 1
        elif self.op == "-" and possibilities:
            new_possibilities = [ -x for x in possibilities]

        output_value = self.expr.selection(memory, variables, nbr_defer, new_possibilities)
        while output_value:

            defer,_,address,value = self.expr.solution(memory)

            #only one try is neccesary to obtain the solution
            if not possibilities or self.op == "*" or self.op == "-":
                break
            #need to verify if the address is in possibilities can not do it with new_possibilities
            #because it restricts the value and not addresses
            elif self.op == "&" and address in possibilities:
                break

            output_value = self.expr.selection(memory, variables, nbr_defer, new_possibilities)

        #child expression can not be generated
        if not output_value:
            return False

        defer,_,address,value = self.expr.solution(memory)

        #check if a cast need to be applied before the deferencement
        if self.op == "*" and defer == 0:
            self.iscast = True
            self.nbr_cast = nbr_defer+1

        return True


    def solution(self,memory):
        pointer_length, address_size, address, value = self.expr.solution(memory)
        if self.op == "&":
            return pointer_length+1, address_size, None, address
        if self.op == "*":
            return pointer_length-1, address_size ,value, memory[value]
        if self.op == "-":
            return pointer_length, address_size, address, -value


    def feedback(self,memory):

        feed = self.expr.feedback(memory)
        char_mode = False
        new_feed = []
        for f in feed:

            pointer_length, address_size, address, value = f.values()
            if self.op == "&":
                if address is not None:
                    f.changeValues(pointer_length+1, address_size, None, address)
                else:
                    feed.remove(f)
            elif self.op == "*":
                if value in memory:
                    f.changeValues(pointer_length-1, address_size ,value, memory[value])
                    if  isinstance(memory[value], str) and memory[value].isalpha():
                        char_mode = True
                else:
                    feed.remove(f)
                if len(f.error_type) < max_error:

                    if not char_mode:
                        #forget to deference
                        new_feed.append(Feedback(pointer_length, address_size, address, value, f.error_type+ [3],f.proba * error_probabilities[3]))
                    if value in memory and memory[value] in memory:
                        #deference too much
                        new_feed.append(Feedback(pointer_length-2, address_size, memory[value], memory[memory[value]], f.error_type + [4],f.proba * error_probabilities[4]))


                    if self.iscast == True:
                        val = value
                        sf = False
                        for n in range(self.nbr_cast):
                            if val in memory:
                                add = val
                                val = memory[val]
                            else:
                                sf = True
                        if sf is not True:
                            #the cast operation do not dereference
                            new_feed.append(Feedback(pointer_length-self.nbr_cast, address_size, add, val, f.error_type + [5],f.proba * error_probabilities[5]))

        return feed + new_feed


    def result_vector(self,memory):
        vector = self.expr.result_vector(memory)
        _,_,address, result = self.solution(memory)
        vector += [address,result]
        return vector

    def get_pointer_length(self):
        pointer_length = self.expr.get_pointer_length()
        if self.op == "&":
            return pointer_length+1
        if self.op == "*":
            if pointer_length == 0:
                return 0
            else:
                return pointer_length-1
        if self.op == "-":
            return pointer_length

class Incr():

    def __init__(self,side,expr,op):
        self.side = side
        self.expr = expr
        self.op = op


    def printExpr(self,nbr_defer=0):
        if not isinstance(self.expr, VariableExpr):
            if self.side == "right":
                return "("+self.expr.printExpr(nbr_defer) +")"+ self.op
            else:
                return self.op + self.expr.printExpr(nbr_defer)
        if self.side == "right":
            return self.expr.printExpr(nbr_defer) + self.op
        else:
            return self.op + self.expr.printExpr(nbr_defer)


    def latex(self, nbr_defer=0):
        if not isinstance(self.expr, VariableExpr):
            if self.side == "right":
                return "("+self.expr.latex(nbr_defer) +")"+ self.op
            else:
                return self.op + self.expr.latex(nbr_defer)
        if self.side == "right":
            return self.expr.latex(nbr_defer) + self.op
        else:
            return self.op + self.expr.latex(nbr_defer)


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):

        if self.side == "left_right":
            side_choice = ["left", "right"]
        elif self.side == "left":
            side_choice = ["left"]
        else:
            side_choice = ["right"]
        random.shuffle(side_choice)

        if self.op == "++--":
            sign_choice = ["++","--"]
        elif self.op == "++":
            sign_choice = ["++"]
        else:
            sign_choice = ["--"]
        random.shuffle(sign_choice)

        #test the different combinations to obtain feasible expression
        for side in side_choice:
            for sign in sign_choice:
                if side == "right":
                    if self.expr.selection(memory, variables, nbr_defer,possibilities):
                        self.side = side
                        self.op = sign
                        return True
                else:
                    if possibilities is None:
                        if self.expr.selection(memory, variables, nbr_defer):
                            self.side = side
                            self.op = sign
                            return True

                    else:
                        address_size = type_conversion["int"]
                        pointer_length = self.expr.get_pointer_length()
                        new_possibilities = []
                        #this class incr/decr a value
                        if pointer_length == 0:
                            #perform the opposite operation to obtain new_possibilities
                            #++value -> --possibilities
                            #--value -> ++possibilities
                            if sign == "++":
                                new_possibilities = [x-1 for x in possibilities]
                            else:
                                new_possibilities = [x+1 for x in possibilities]

                            if self.expr.selection(memory, variables, nbr_defer,new_possibilities):
                                self.side = side
                                self.op = sign
                                return True

                        #this class incr/decr a pointer
                        else:
                            #perform the opposite operation to obtain new_possibilities
                            if sign == "++":
                                new_possibilities = [x-address_size for x in possibilities]
                            else:
                                new_possibilities = [x+address_size for x in possibilities]

                            if self.expr.selection(memory, variables, nbr_defer,new_possibilities):
                                self.side = side
                                self.op = sign
                                return True

        return False



    def solution(self,memory):
        pointer_length, address_size, address, value = self.expr.solution(memory)
        if self.side == "right":
            return pointer_length, address_size, address, value
        else:
            if pointer_length == 0:
                if self.op == "++":
                    return pointer_length, address_size, None, value+1
                else:
                    return pointer_length, address_size, None, value-1
            else:
                if self.op == "++":
                    return pointer_length, address_size, None,value+address_size
                else:
                    return pointer_length, address_size, None,value-address_size


    def feedback(self,memory):
        feed = self.expr.feedback(memory)
        new_feed = []
        for f in feed:
            pointer_length, address_size, address, value = f.values()
            if self.side == "right":
                if self.op == "++":
                    if pointer_length == 0:
                        #right side return value after incr/decr and not before
                        new_feed.append(Feedback(pointer_length, address_size, address, value+1, f.error_type + [6],f.proba * error_probabilities[6]))
                    else:
                        #right side return value after incr/decr and not before
                        new_feed.append(Feedback(pointer_length, address_size, None,value+address_size, f.error_type + [6],f.proba * error_probabilities[6]))
                else:
                    if pointer_length == 0:
                        #right side return value after incr/decr and not before
                        new_feed.append(Feedback(pointer_length, address_size, address, value-1, f.error_type + [6],f.proba * error_probabilities[6]))
                    else:
                        #right side return value after incr/decr and not before
                        new_feed.append(Feedback(pointer_length, address_size, None,value-address_size, f.error_type + [6],f.proba * error_probabilities[6]))

            else:
                #right side return value before incr/decr and not after
                new_feed.append(Feedback(pointer_length, address_size, address, value,f.error_type + [7],f.proba * error_probabilities[7]))
                if pointer_length == 0:
                    if self.op == "++":
                        f.changeValues(pointer_length, address_size, address, value+1)
                        #incr by the address size instead of 1
                        new_feed.append(Feedback(pointer_length, address_size, None,value+address_size,f.error_type + [8],f.proba * error_probabilities[8]))
                    else:
                        f.changeValues(pointer_length, address_size, address, value-1)
                        #decr by the address size instead of 1
                        new_feed.append(Feedback(pointer_length, address_size, None,value-address_size,f.error_type + [8],f.proba * error_probabilities[8]))
                else:
                    if self.op == "++":
                        f.changeValues(pointer_length, address_size, address, value+address_size)
                        #incr by 1 instead of address size
                        new_feed.append(Feedback(pointer_length, address_size, address, value+1,f.error_type + [9],f.proba * error_probabilities[9]))
                    else:
                        f.changeValues(pointer_length, address_size, address, value-address_size)
                        #decr by 1 instead of address size
                        new_feed.append(Feedback(pointer_length, address_size, address, value-1,f.error_type + [9],f.proba * error_probabilities[9]))
        return feed + new_feed

    def result_vector(self,memory):
        vector = self.expr.result_vector(memory)
        _,_,address, result = self.solution(memory)
        vector += [address,result]
        return vector

    def get_pointer_length(self):
        return self.expr.get_pointer_length()


class Binop():

    def __init__(self, op, left_expr, right_expr):
        self.op = op
        self.left_expr = left_expr
        self.right_expr = right_expr


    def printExpr(self,nbr_defer=0):
        return self.left_expr.printExpr(nbr_defer) +" "+ self.op +" "+ self.right_expr.printExpr(nbr_defer)


    def latex(self, nbr_defer=0):
        return self.left_expr.latex(nbr_defer) +" "+ self.op +" "+ self.right_expr.latex(nbr_defer)


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        if possibilities == None:
            if self.op == "+-":
                i = random.randrange(0,2,1)
                if i == 0:
                    self.op = "+"
                else:
                    self.op = "-"
            if not self.left_expr.selection(memory, variables, nbr_defer):
                return False
            if not self.right_expr.selection(memory, variables, nbr_defer):
                return False
            return True
        #possibilities is given
        else:
            if self.op == "=":
                #only the right side is influanced by possibilities
                if not self.right_expr.selection(memory, variables, nbr_defer,possibilities):
                    return False
                if not self.left_expr.selection(memory, variables, nbr_defer):
                    return False
                return True

            #find the type of addition or subtraction
            # value +- value
            # address +- value
            # address - address
            l_pointer_length = self.left_expr.get_pointer_length()
            r_pointer_length= self.right_expr.get_pointer_length()

            # address - address
            if l_pointer_length > 0 and r_pointer_length > 0:
                self.op = "-"
                case = 1
            # address +- value
            elif l_pointer_length > 0 and r_pointer_length == 0:
                case = 2
            #value + address because value - address is not possible
            elif l_pointer_length == 0 and r_pointer_length > 0:
                self.op = "+"
                case = 3
            #value +- value
            else:
                case = 4

            copy_variables = copy.copy(variables)

            while True:
                # address - address
                if case == 1:
                    if not self.left_expr.selection(memory, copy_variables, nbr_defer):
                        return False

                    l_pointer_length, l_address_size,l_address,l_value= self.left_expr.solution(memory)

                    new_possibilities = []
                    for x in possibilities:
                        if l_value-x != l_value:#this condition is used to be sure to have different expr in both side
                            new_possibilities.append((l_value-x*l_address_size))

                    if self.right_expr.selection(memory, variables, nbr_defer,new_possibilities):
                        return True

                # address +- value
                elif case == 2:
                    if not self.left_expr.selection(memory, copy_variables, nbr_defer):
                        return False

                    l_pointer_length, l_address_size,_,value1 = self.left_expr.solution(memory)

                    if self.op == "+-":
                        self.op = random.choice(["+","-"])

                    new_possibilities = []
                    for x in possibilities:
                        if self.op == "+":
                            new_possibilities.append(int((x-value1)/l_address_size))
                        else:
                            new_possibilities.append(int((value1-x)/l_address_size))
                    if not self.right_expr.selection(memory, variables, nbr_defer,new_possibilities):
                        return False
                    return True

                #value + address
                elif case == 3:
                    if not self.right_expr.selection(memory, copy_variables, nbr_defer):
                        return False

                    r_pointer_length, r_address_size,_,value1 = self.left_expr.solution(memory)

                    new_possibilities = []
                    for x in possibilities:
                        ssibilities.append(int((x-value1)/l_address_size))

                    if not self.left_expr.selection(memory, variables, nbr_defer,new_possibilities):
                        return False
                    return True

                #value +- value
                elif case == 4:
                    if not self.left_expr.selection(memory, copy_variables, nbr_defer):
                        return False

                    l_pointer_length, l_address_size,l_address,l_value= self.left_expr.solution(memory)

                    #compute child possibilities
                    #if op not chosen yet (either + or -) computes possibilities for both and choose one after
                    new_possibilities = []
                    for x in possibilities:
                        if self.op == "+" or self.op == "+-":
                            if x-l_value != l_value:
                                new_possibilities.append(x-l_value)
                        if self.op == "-"or self.op == "+-":
                            if l_value-x != l_value:
                                new_possibilities.append(l_value-x)

                    if self.right_expr.selection(memory, variables, nbr_defer,new_possibilities):

                        if self.op == "+-":
                            r_pointer_length, r_address_size,r_address,r_value= self.right_expr.solution(memory)

                            #Choose an operator and randomise not to favour one
                            c = random.choice([0,1])
                            if c == 0:
                                if l_value + r_value in possibilities:
                                    self.op = "+"
                                else:
                                    self.op = "-"
                            else:
                                    if l_value - r_value in possibilities:
                                        self.op = "-"
                                    else:
                                        self.op = "+"

                        return True

                    return False




    def solution(self,memory):
        l_pointer_length, l_address_size, l_address, l_value = self.left_expr.solution(memory)
        r_pointer_length, r_address_size, r_address, r_value = self.right_expr.solution(memory)
        if self.op == "=":
            return r_pointer_length, r_address_size, r_address, r_value
        if l_pointer_length == 0 and r_pointer_length == 0:

            if self.op == "+":
                return 0, l_pointer_length, None, l_value + r_value
            elif self.op == "-":
                return 0, l_pointer_length, None, l_value - r_value
        elif l_pointer_length > 0 and r_pointer_length > 0:
            return 0, l_address_size, None, (l_value-r_value)/l_address_size
        else:
            if l_pointer_length > 0:
                if self.op == "+":
                    return l_pointer_length, l_address_size, None, l_value+r_value*l_address_size
                elif self.op == "-":
                    return l_pointer_length, l_address_size, None, l_value-r_value*l_address_size
            else:
                if self.op == "+":
                    return r_pointer_length, r_address_size, None, r_value+l_value*r_address_size
                elif self.op == "-":
                    return r_pointer_length, r_address_size, None, r_value-l_value*r_address_size


    def feedback(self,memory):
        l_feed = self.left_expr.feedback(memory)
        r_feed = self.right_expr.feedback(memory)
        feed = []
        for l_f in l_feed:
            for r_f in r_feed:
                l_pointer_length, l_address_size, l_address, l_value = l_f.values()
                r_pointer_length, r_address_size, r_address, r_value = r_f.values()

                if self.op == "=":
                    feed.append(Feedback(r_pointer_length, r_address_size, r_address, r_value, r_f.error_type, r_f.proba))

                elif len(l_f.error_type) + len(r_f.error_type) < max_error:
                    if l_pointer_length == 0 and r_pointer_length == 0:

                        if self.op == "+":
                            #correct operation
                            feed.append(Feedback( 0, l_pointer_length, None, l_value + r_value,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                            #addition of two values interpreted as an address and a value
                            feed.append(Feedback( 0, l_pointer_length, None, l_value + r_value*l_address_size,l_f.error_type + r_f.error_type + [10],l_f.proba*r_f.proba*error_probabilities[10]))
                            #addition of two values interpreted as an address and a value
                            feed.append(Feedback( 0, l_pointer_length, None, l_value*r_address_size + r_value,l_f.error_type + r_f.error_type+ [10],l_f.proba*r_f.proba*error_probabilities[10]))
                        elif self.op == "-":
                            feed.append(Feedback( 0, l_pointer_length, None, l_value - r_value,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                            #subtraction of two values interpreted as an address and a value
                            feed.append(Feedback( 0, l_pointer_length, None, l_value - r_value*l_address_size,l_f.error_type + r_f.error_type + [10],l_f.proba*r_f.proba*error_probabilities[10]))
                            #subtraction of two values interpreted as a difference of addresses
                            feed.append(Feedback( 0, l_pointer_length, None, (l_value - r_value)/l_address_size,l_f.error_type + r_f.error_type+ [11],l_f.proba*r_f.proba*error_probabilities[11]))
                    elif l_pointer_length > 0 and r_pointer_length > 0:
                        #correct operation
                        feed.append(Feedback( 0,l_address_size, None, (l_value-r_value)/l_address_size,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                        #two addresses forget to divide by the address size
                        feed.append(Feedback( 0, l_pointer_length, None, (l_value - r_value),l_f.error_type + r_f.error_type+ [14],l_f.proba*r_f.proba*error_probabilities[14]))
                        #two addresses interpreted as an address and a value
                        feed.append(Feedback( 0, l_pointer_length, None, (l_value - r_value*l_address_size),l_f.error_type + r_f.error_type+ [15],l_f.proba*r_f.proba*error_probabilities[15]))
                    else:
                        if l_pointer_length > 0:
                            if self.op == "+":
                                #correct operation
                                feed.append(Feedback(l_pointer_length, l_address_size, None, l_value+r_value*l_address_size,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                                #addition of an address and a value interpreted as two values
                                feed.append(Feedback(l_pointer_length, l_address_size, None, l_value+r_value,l_f.error_type + r_f.error_type+[12],l_f.proba*r_f.proba*error_probabilities[12]))
                            elif self.op == "-":
                                #correct operation
                                feed.append(Feedback(l_pointer_length, l_address_size, None, l_value-r_value*l_address_size,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                                #subtraction of an address and a value interpreted as two values
                                feed.append(Feedback(l_pointer_length, l_address_size, None, l_value-r_value,l_f.error_type + r_f.error_type+[12],l_f.proba*r_f.proba*error_probabilities[12]))
                                #subtraction of an address and a value interpreted as two addresses
                                feed.append(Feedback(l_pointer_length, l_address_size, None, (l_value-r_value)/l_address_size,l_f.error_type + r_f.error_type+[13],l_f.proba*r_f.proba*error_probabilities[13]))
                        else:
                            if self.op == "+":
                                #correct operation
                                feed.append(Feedback( r_pointer_length, r_address_size, None, r_value+l_value*r_address_size,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))
                                #addition of an address and a value interpreted as two values
                                feed.append(Feedback(l_pointer_length, l_address_size, None, l_value+r_value,l_f.error_type + r_f.error_type+[12],l_f.proba*r_f.proba*error_probabilities[12]))
                            elif self.op == "-":
                                #correct operation
                                feed.append(Feedback( r_pointer_length, r_address_size, None, r_value-l_value*r_address_size,l_f.error_type + r_f.error_type,l_f.proba*r_f.proba))

        return feed

    def result_vector(self,memory):
        vector1 = self.left_expr.result_vector(memory)
        vector2 = self.right_expr.result_vector(memory)
        vector = vector1 + vector2
        _,_,address, result = self.solution(memory)
        vector += [address,result]
        return vector

    def get_pointer_length(self):
        l_pointer_length = self.left_expr.get_pointer_length()
        r_pointer_length = self.right_expr.get_pointer_length()
        if l_pointer_length > r_pointer_length:
            return l_pointer_length
        else:
            return r_pointer_length


class Cast():

    def __init__(self,type,cast_stars, expr):
        self.type = type
        self.cast_stars = cast_stars
        self.expr = expr


    def printExpr(self,nbr_defer=0):
        if isinstance(self.expr, Binop):
            return "("+ self.type + "*" * self.cast_stars + ") (" + self.expr.printExpr(nbr_defer) + ")"
        else:
            return "("+ self.type + "*" * self.cast_stars + ")" + self.expr.printExpr(nbr_defer)


    def latex(self, nbr_defer=0):
        if isinstance(self.expr, Binop):
            return "("+ self.type + "*" * self.cast_stars + ") (" + self.expr.latex(nbr_defer) + ")"
        else:
            return "("+ self.type + "*" * self.cast_stars + ")" + self.expr.latex(nbr_defer)


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        if nbr_defer > self.cast_stars:
            if not self.expr.selection(memory, variables, nbr_defer, possibilities):
                return False
        else:
            if not self.expr.selection(memory, variables, self.cast_stars, possibilities):
                return False

        if self.cast_stars == 0:
            _,_,_, value = self.expr.solution(memory)
            #if value is supperior than max of short (normally it will not append)
            if value > (4**(4*type_conversion["short"]))/2 - 1:
                if self.type == "long_short":
                    self.type ="long"
                elif self.type == "short":
                    return False

        if self.type == "long_short":
            self.type = random.choice(["long","short"])

        return True


    def solution(self,memory):
        pointer_length, address_size, address, value = self.expr.solution(memory)
        return pointer_length+self.cast_stars, type_conversion[self.type], address, value


    def feedback(self,memory):
        feed = self.expr.feedback(memory)
        new_feed = []
        for f in feed:
            pointer_length, address_size, address, value = f.values()
            #correct solution
            f.changeValues(pointer_length+self.cast_stars, type_conversion[self.type], address, value)
            #error in casting address size (use previous size)
            new_feed.append(Feedback(pointer_length+self.cast_stars, address_size, address, value,f.error_type +[16],f.proba*error_probabilities[16]))
            for t in type_conversion.values():
                if t != type_conversion[self.type] and t != address_size and t != 1:
                    #error in casting address size (use an other wrong size)
                    new_feed.append(Feedback(pointer_length+self.cast_stars, t, address, value,f.error_type +[16],f.proba*error_probabilities[16]))
            val = value
            add = address
            sf = False
            for n in range(self.cast_stars):
                if val in memory and memory[val] in memory:
                    add = memory[val]
                    val = memory[memory[val]]
                else:
                    sf = True
            if sf is not True:
                #cast operation do not dereference
                new_feed.append(Feedback(pointer_length-self.cast_stars, address_size, add, val, f.error_type + [17],f.proba*error_probabilities[17]))
        return feed + new_feed

    def result_vector(self,memory):
        vector = self.expr.result_vector(memory)
        _,_,address, result = self.solution(memory)
        return (vector + [address,result])

    def get_pointer_length(self):
        pointer_length = self.expr.get_pointer_length()
        return pointer_length + self.cast_stars


class Array():

    def __init__(self,expr,index):
        self.expr = expr
        self.index = index


    def printExpr(self,nbr_defer=0):
        if isinstance(self.expr, Cast):
            return "(" + self.expr.printExpr(nbr_defer) + ")" + "[" +self.index.printExpr(nbr_defer) + "]"
        else:
            return self.expr.printExpr(nbr_defer) + "[" +self.index.printExpr(nbr_defer) + "]"



    def latex(self, nbr_defer=0):
        if isinstance(self.expr, Cast):
            return "(" + self.expr.latex(nbr_defer) + ")" + "[" +self.index.latex(nbr_defer) + "]"
        else:
            return self.expr.latex(nbr_defer) + "[" +self.index.latex(nbr_defer) + "]"


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        new_possibilities = []

        #select the address part (address[index]) without retriction of possibilities
        if not self.expr.selection(memory, copy.copy(variables), nbr_defer):
            return False

        #compute the possibilities for the index child given the previous address
        if possibilities is not None:
            _,address_size,_, address = self.expr.solution(memory)
            addresses_memory = list(memory.keys())
            for a in addresses_memory:
                i = int((a - address) / address_size)
                if memory[address+i*address_size] in possibilities:
                    new_possibilities.append(i)
                if isinstance(memory[address+i*address_size], str) and memory[address+i*address_size].isalpha() and ord(memory[address+i*address_size]) in possibilities:
                    new_possibilities.append(i)
        else:
            _,address_size,_, address = self.expr.solution(memory)
            addresses_memory = list(memory.keys()) #give all the possible index for the array to be in memory
            for a in addresses_memory:
                i =int( (a - address) / address_size)
                new_possibilities.append(i)

        #if no index can be choosen
        if not new_possibilities:
            return False

        if not self.index.selection(memory, variables, nbr_defer, new_possibilities):
            return False

        return True


    def solution(self,memory):
        e_pointer_length, e_address_size, e_address, e_value = self.expr.solution(memory)
        i_pointer_length, i_address_size, i_address, i_value = self.index.solution(memory)
        return_value = memory[e_value+i_value*e_address_size]
        add = e_value+i_value*e_address_size
        if isinstance(return_value, str) and return_value.isalpha():
            return e_pointer_length-1, e_address_size ,add, ord(return_value)
        else:
            return e_pointer_length-1, e_address_size ,add, return_value

    def feedback(self,memory):
        e_feed = self.expr.feedback(memory)
        i_feed = self.index.feedback(memory)
        feed = []
        for e_f in e_feed:
            for i_f in i_feed:
                e_pointer_length, e_address_size, e_address, e_value = e_f.values()
                i_pointer_length, i_address_size, i_address, i_value = i_f.values()
                add = e_value+i_value*e_address_size
                if add in memory:
                    return_value = memory[add]
                else:
                    continue
                    return_value = None
                if isinstance(return_value, str) and return_value.isalpha():
                    feed.append(Feedback(e_pointer_length-1, e_address_size ,add, ord(return_value),e_f.error_type + i_f.error_type,e_f.proba*i_f.proba))

                else:
                    feed.append(Feedback(e_pointer_length-1, e_address_size ,add, return_value,e_f.error_type + i_f.error_type,e_f.proba*i_f.proba))

        return feed

    def result_vector(self,memory):
        vector1 = self.expr.result_vector(memory)
        vector2 = self.index.result_vector(memory)
        vector = vector1 + vector2
        _,_,address, result = self.solution(memory)
        vector += [address,result]
        return vector

    def get_pointer_length(self):
        pointer_length = self.expr.get_pointer_length()
        return pointer_length-1

class Function():

    def __init__(self,function,expr):
        self.expr = expr
        self.function = function


    def printExpr(self,nbr_defer=0):
        if self.function == "printf":
            return "printf(\"%s\", " + self.expr.printExpr(nbr_defer) + ")"


    def latex(self, nbr_defer=0):
        if self.function == "printf":
            return "printf(\"\%s\", " + self.expr.printExpr(nbr_defer) + ")"


    def selection(self, memory, variables, nbr_defer = 0, possibilities = None):
        if self.function == "printf":
            while self.expr.selection(memory, variables, nbr_defer):
                _, _, _, value = self.expr.solution(memory)
                if not possibilities:
                    break
                elif value in possibilities:
                    break
            if not variables:
                return False
            return True
        return False


    def solution(self,memory):
        if self.function == "printf":
            pointer_length, address_size, address, value = self.expr.solution(memory)
            i=0
            memory[value]
            while value in memory.keys():
                value += address_size
                i += 1
            i += 1
            return 0, 0 ,None, i

    def feedback(self,memory):
        if self.function == "printf":
            pointer_length, address_size, address, value = self.expr.solution(memory)
            i=0
            memory[value]
            while value in memory.keys():
                value += address_size
                i += 1
            i += 1
            return [Feedback(0, 0 ,None, i,[],1)]

    def result_vector(self,memory):
        if self.function == "printf":
            vector = self.expr.result_vector(memory)
            _,_,address, result = self.solution(memory)
            vector += [address,result]
            return vector

    def get_pointer_length(self):
        if self.function == "printf":
            return 0
