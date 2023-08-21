import operator

"""
Associate each error with an explanation text for the student
"""
error_conversion = {
    "0" : "Vous avez la bonne reponse",
    "1" : "La variable est de type entier. Sa valeur est donc celle stockee dans la memoire et non son adresse.",
    "2" : "La variable est un pointeur sur un entier. Sa valeur est donc l'adresse de la variable pointee et non de sa valeur.",
    "3" : "Vous avez oublie de deferencer une fois.",
    "4" : "Vous avez deference trop de fois.",
    "5" : "L'operation cast n'est pas un deferencement.",
    "6" : "L'operation d'incrementation ou de decrementation est à droite, le resultat de l'operation est la valeur de la variable avant l'operation.",
    "7" : "L'operation d'incrementation ou de decrementation est à gauche, le resultat de l'operation est la valeur de la variable apres l'operation.",
    "8" : "L'operation d'incrementation ou de decrementation s'applique ici à un entier et non une adresse.",
    "9" : "L'operation d'incrementation ou de decrementation s'applique ici à une adresse et non un entier.",
    "10" : "Avez-vous utilise la bonne formule ? L'operation d'addition ou de soustraction s'effectue sur deux entiers.",
    "11" : "Avez-vous utilise la bonne formule ? L'operation d'addition ou de soustraction s'effectue sur deux entiers.",
    "12" : "Avez-vous utilise la bonne formule ? L'operation d'addition ou de soustraction s'effectue sur une adresse et une valeur. ",
    "13" : "Avez-vous utilise la bonne formule ? L'operation d'addition ou de soustraction s'effectue sur une adresse et une valeur. ",
    "14" : "Vous avez oublie de diviser par sizeof(element pointe)",
    "15" : "Avez-vous utilise la bonne formule ? L'operation de soustraction s'effectue sur deux adresses.",
    "16" : "Attention vous avez utilise la mauvaise taille d'adresse",
    "17" : "L'operation cast n'est pas un deferencement.",
}


"""
For a given expression generate the feedback
Input : the expression and the memory
Output: dictionnary of pair value (answer, feedback text for this answer)
"""
def createFeedback(expr, memory):
    feed =expr.feedback(memory)

    #sort and then select the first element (->most likely)
    if feed and isinstance(feed[0].value, str) and feed[0].value.isalpha():
        feed.sort(key=lambda x: (ord(x.value), x.proba), reverse=True)
    else:
        feed.sort(key=lambda x: (x.value, x.proba), reverse=True)

    #Create the text feedback for each answer values
    return_feedback = {}
    for f in feed:
        if f.value in return_feedback:#if the value already exist it means this error is not the more likely
            continue

        length = len(f.error_type)
        if length == 0:#correct solution
            text = error_conversion["0"]
        elif length == 1:#1 error
            text = "Vous avez probablement fait 1 erreur:\n"
        else:#more errors
            text = "Vous avez probablement fait " + str(length) + " erreurs:\n"

        for i in range(length) :
            text += error_conversion[str(f.error_type[i])]#predefined text
            text += "\n"
        return_feedback[f.value] = text

    return return_feedback
