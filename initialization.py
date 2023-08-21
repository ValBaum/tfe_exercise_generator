import random
import string
import math

from parameters import *
MAX_CAST = 4
ADDRESS_SIZE = 4 #int
LIST_OF_WORDS = ["informatique","geraldine","invariant","examen","challenge","valentin","ordinateur"]

"""
One class for each different type of variables
"""
class Simple_variable:
    def __init__(self,type,name,MAX_CAST):
        self.type = type
        self.name = name
        self.MAX_CAST =  MAX_CAST
        self.address = None

class Pointer_variable:
    def __init__(self,type,name,pointer_length,MAX_CAST,pointing_variable):
        self.type = type
        self.name = name
        self.pointer_length = pointer_length
        self.MAX_CAST =  MAX_CAST
        self.pointing_variable = pointing_variable

class Array_variable:
    def __init__(self,type,name,array_length):
        self.type = type
        self.name = name
        self.array_length = array_length
        self.begin_address = None

class Char_variable:
    def __init__(self,name,value,variable_reference = None, variable_shift = None):
        self.name = name
        self.value = value
        self.variable_reference = variable_reference #name
        self.variable_shift = variable_shift
        self.begin_address = None

"""
Create a memory.
Input : the list of the variables ("variables")
Return a dictionnary with the key equal to a memory address and with corresponding value equal to the value
stored in the memory address
"""
def createMemory(variables):

    memory = {}
    length = [0] * MAX_NBR_MEMORY_BLOCKS
    char_length = []

    # find the memory interval of MEMORY_RANGE size that fit in lower/upper bound
    lowerbound_memory = random.randrange(MAX_MEMORY_INTERVAL[0],MAX_MEMORY_INTERVAL[1]-MEMORY_RANGE, ADDRESS_SIZE)
    upperbound_memory = lowerbound_memory + MEMORY_RANGE


    # assign arrays to memory blocks to create large enough blocks
    # and the char length is used to set the distance between two blocks
    for v in variables:
        if isinstance(v, Array_variable) and v.array_length > length[0]:
            i = random.randrange(0,MAX_NBR_MEMORY_BLOCKS,1)
            length[i] =  v.array_length
        if isinstance(v, Char_variable) and v.value != None:
            char_length.append(len(v.value)+1)

    # assign the other address (not part of the array) to blocks
    total_char_length = sum(char_length)
    for _ in range(NBR_VISIBLE_ADDRESS - sum(length)):
        i = random.randrange(0,MAX_NBR_MEMORY_BLOCKS,1)
        length[i] += 1

    # remove a memory block of size 0
    length = [x for x in length if x !=0]

    # place the first memory block in the memory interval
    for i in range(length[0]):
        memory[lowerbound_memory+ADDRESS_SIZE*i] = "/"

    new_lowerbound = lowerbound_memory + ADDRESS_SIZE*length[0]

    # place the last memory block in the memory interval
    for i in range(length[len(length)-1]):
        memory[upperbound_memory-ADDRESS_SIZE*i] = "/"

    new_upperbound = upperbound_memory-ADDRESS_SIZE*length[len(length)-1]

    remaining_address = NBR_VISIBLE_ADDRESS -length[0] - length[len(length)-1]

    # place the middle memory blocks in the memory interval
    # and check if enough free space for char arrays
    for i in range(len(length)-2):
        address= random.randrange(new_lowerbound,new_upperbound+1+ADDRESS_SIZE-remaining_address*ADDRESS_SIZE-total_char_length,ADDRESS_SIZE)
        if total_char_length > 0:
            interval = (address - new_lowerbound) / ADDRESS_SIZE
            if interval > total_char_length:
                total_char_length = 0
                char_length = []
            else:
                for x in char_length[:]:
                    if interval > x:
                        char_length.remove(x)
                        total_char_length - x
                        interval - x

        #notify that the value at the address is empty ("/")
        for y in range(length[i+1]):
            memory[address+ADDRESS_SIZE*y] = "/"

        remaining_address -= length[i+1]
        new_lowerbound = address + ADDRESS_SIZE * length[i+1]


    if total_char_length > 0:
        interval = new_upperbound - new_lowerbound
        if interval > total_char_length:
            total_char_length = 0
            char_length = []
        else:#not enough place for the char arrays
            print("No free space for the char array")
            return {}
    memory = dict(sorted(memory.items()))
    memory_address = list(memory.keys())

    #assign addresses to array variables
    for v in variables:
        if isinstance(v,Array_variable):
            m = list(memory.keys())
            count = 1
            possi_begin = []
            begin = m[0]
            for i in range(NBR_VISIBLE_ADDRESS-1):
                if m[i]+ADDRESS_SIZE ==  m[i+1]:
                    count += 1
                    if count >= v.array_length:
                        possi_begin.append(begin)
                        begin = m[i-v.array_length+2]
                else:
                    count = 1
                    begin = m[i+1]
            v.begin_address = random.choice(possi_begin)
            memory_address.remove(begin)

    #assign addresses to simple variables
    for v in variables:
        if isinstance(v,Simple_variable):
            address = random.choice(memory_address)
            memory_address.remove(address)
            v.address = address


    #Create the pointer path
    memory_address = list(memory.keys())
    address = variables[0].address
    memory_address.remove(address)
    for v in variables:
        if isinstance(v,Simple_variable) and v is not variables[0]:
                memory_address.remove(v.address) #second variable can not be part of pointer path
    for _ in range(variables[0].MAX_CAST):

        new_address = random.choice(memory_address)
        memory_address.remove(new_address)
        memory[address] = new_address
        address = new_address


    #fill the remaining empty addresses ("/")
    fill_memory(memory,variables)


    return memory



"""
Create all the variables.
Input : repartion of the variables ([nbr of simple, nbr of pointer, nbr of array, nbr of char])
Return a list of all the variables
"""
def createVariables(var_repartition):
    variables = []
    # Variables name
    name_simple_var = list(string.ascii_lowercase)
    name_pointer = list(("ptr","tab"))
    name_char = list(string.ascii_uppercase)

    #simple variable
    for i in range(var_repartition[0]):
        if i == 0:# simple variable that can be cast "MAX_CAST" times into a pointer
            name = random.choice(name_simple_var)
            name_simple_var.remove(name)
            v = Simple_variable("int",name,MAX_CAST)
            variables.append(v)
        else:
            # simple variable with no cast
            name = random.choice(name_simple_var)
            name_simple_var.remove(name)
            v = Simple_variable("int",name,0)
            variables.append(v)

    # pointer variables pointing to simple variable
    for i in range(var_repartition[1]):
        r = random.randrange(0,2,1)
        if r == 0 and name_pointer:
            name = random.choice(name_pointer)
            name_pointer.remove(name)
        else:
            name = random.choice(name_simple_var)
            name_simple_var.remove(name)
        v = Pointer_variable("int",name,1,variables[i].MAX_CAST,variables[i])
        variables.append(v)

    #aray variables
    for _ in range(var_repartition[2]):
        name = random.choice(name_simple_var)
        name_simple_var.remove(name)
        variables.append(Array_variable("int",name,4))

    #char variables
    for i in range(var_repartition[3]):
        if i == 0:#char containing the string
            name = random.choice(name_char)
            name_char.remove(name)
            value = random.choice(LIST_OF_WORDS)
            len_value = len(value)
            variables.append(Char_variable(name,value))
            previous_name = name
        else:#char pointing to the other variable
            name = random.choice(name_char)
            name_char.remove(name)
            max_size = len_value-(var_repartition[3]-i-1)
            size = random.randrange(0,max_size,1)
            len_value -= size
            variables.append(Char_variable(name,None, previous_name,size))
            previous_name = name

    return variables

"""
Create the exercise initialization/declaration in a string format
Input : memory(dict), variables(List)
Output : a string containing the initialization
"""
def printInitialization(variables,memory):

    s ="int "
    array_string = ""
    char_string1 = ""
    char_string2 = ""
    for v in variables:
        if isinstance(v,Simple_variable):
            s +=  v.name + ", "
        elif isinstance(v,Pointer_variable):
            s += "*" * v.pointer_length +  v.name
            if v.pointing_variable is not None:
                s += " = &" +v.pointing_variable.name
            s += ", "
        elif isinstance(v,Array_variable):
            array_string += v.type + " " + v.name +"[] = {"
            for i in range(v.array_length):
                array_string += str(memory[v.begin_address + ADDRESS_SIZE * i])
                if i+1 == v.array_length:
                    array_string += "};"
                else:
                    array_string += ","
        elif isinstance(v,Char_variable):
            if v.value:
                char_string1 += "char *" + v.name + " = \"" + v.value +"\","
            else:
                char_string2 += " *"+ v.name + " = " + v.variable_reference +" + "+ str(v.variable_shift)+","
    s = s[:-2] + ';'
    char_string2 = char_string2[:-1] + ';'
    return s + "\n" + array_string + "\n" + char_string1+ char_string2


"""
Print the memory in the console
Input : memory(dict), variables(List)
"""
def printMemory(memory, variables):

    form="{:<11}{:<11}{:<11}"
    print(form.format("variable :","address :","value :"))
    previous_address = -1
    for address, value in reversed(memory.items()):
        a = ""
        for x in variables:
            if isinstance(x,Simple_variable) and x.address == address:
                a += x.name + " "
            elif isinstance(x,Array_variable) and x.begin_address == address:
                a += x.name + "[0]"
        if previous_address == address + ADDRESS_SIZE:
            print(form.format(a,address,value))
        else:
            print(form.format("","",""))
            print(form.format(a,address,value))
        previous_address = address


"""
Print the memory in the console
Input : memory(dict), variables(List)
Output : a string containing the memory image in a latex format
"""
def memoryLatex(memory, variables):

    previous_address = -1
    s=""
    for address, value in reversed(memory.items()):
        a = ""
        for x in variables:
            if isinstance(x,Simple_variable) and x.address == address:
                a += x.name + " "
            elif isinstance(x,Array_variable) and x.begin_address == address:
                a += x.name + "[0]"
        if previous_address == address + ADDRESS_SIZE:
            s += a + " & " + str(address) + " & " + str(value) + "\\\ \cline{3-3}\n"
        else:
            if not s:
                s="\cline{3-3}\n"
            else:
                s +=   " & " +  " & " + "..." + "\\\ \cline{3-3}\n"
            s += a + " & " + str(address) + " & " + str(value) + "\\\ \cline{3-3}\n"
        previous_address = address
    return s


"""
Fill the empty address value ("/") with number
Input : memory(dict), variables(List)
"""
def fill_memory(memory,variables):
    memory_address = list(memory.keys())
    number = range(1,6)
    for v in variables:
        if isinstance(v,Simple_variable) and memory[v.address] == "/":
            memory[v.address] = random.choice(number)
    for key,value in memory.items():
        if value == "/":
            i = random.randrange(0,2,1)
            if i == 0:
                memory[key] = random.choice(memory_address)
            else:
                memory[key] = random.choice(number)

"""
Create the memory representation of char variables
as they are not appearing in the other memory
"""
def create_char_memory(variables):
    char_memory = {}
    for v in variables:
        if isinstance(v, Char_variable) and v.value != None:
            v.begin_address = -1*len(v.value)
            for i in range(len(v.value)):
                char_memory[-1*(i+1)] = v.value[len(v.value)-1-i]
            break
    return char_memory
