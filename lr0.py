from prettytable import PrettyTable #Libreria para imprimir la tabla al final 
import sys #Libreria para usar los argumentos de la linea de comando

#Leer el contenido de la GLC a analizar 
#f = open("zazabzbz.cfg", "r")
f = open(sys.argv[1], "r")
reglas=[]
lambdas=[]
reglaSaLambda=0

for rule in f:
    ruleList = rule.replace("\n","").split('->')    
    if ruleList[1]=="/" and ruleList [0]!= "S":
        lambdas.append(ruleList[0])
    elif ruleList[1]=="/" and ruleList [0]== "S":
       reglaSaLambda=1
    else:
        ruleList.append(0) #El tercer elemento de la lista representa el cursor
        reglas.append(ruleList)

for rule in reglas:
    for elem in lambdas:
        if elem in rule[1]:
            if rule[0]=="S" and rule[1]==elem:
                reglaSaLambda=1
            else:
                reglas.append([rule[0],rule[1].replace(elem,""),0])
    
reglas.append(['$',"S",0]) #Agregamos la regla S' --> S (representando S' con $)

#Funcion que elimina reglas repetidas de una lista 
def reglasRepetidas(r):
    newlist =[]
    for elem in r:
        if not(elem in newlist):
            newlist.append(elem)
    newlist.reverse()
    return newlist

#Funcion que nos dice si un simbolo es terminal  
def esNoTerminal (x):
    return x.istitle() or x=="$"

#Funcion que nos regresa las reglas derivadas a partir de la lectura del cursor
def derivacion(r):
    if (esFinal(r)):
        return [r]
    
    reglasEstado=[]
    lol=r[1][r[2]]
    if(esNoTerminal(r[1][r[2]])):
       for x in reglas:
           if( x[0] == r[1][r[2]] ):
               reglasEstado.append(x)  
    for y in reglasEstado:
        reglasEstado=reglasEstado+derivacion(y)
        
    reglasEstado.append(r)
    return reglasEstado

#Funcion que nos dice si el conjunto de reglas de un estado pasa la prueba DK
def reglaDK(rul):
    reglas =[]
    reglas.extend(rul)
    lecturaFinal=[] 
    if(len(rul)==1 and esFinal(rul[0])):
        return True,[],[]

    
    for r in reglas:
        r[2]=r[2]+1
        if esFinal(r):
            lecturaFinal.append(r)
            
    for rl in rul:
        for final in lecturaFinal:
            if rl[1][rl[2]-1] == final[1][final[2]-1] and rl!= final:
                return  (False,rl,final)
    
    for r in rul:
        r[2]=r[2]-1
        
    return (True,[],[])
        
        
     
#Funcion que nos dice si una regla tiene el apuntador al final 
def esFinal(r):
    return(r[2]==len(r[1]))
      
#Funcion principal de generacion de estado
def nuevoEstado(r,i):
    idE=i
    estados=[]
    e=[]
    transiciones={}
    rules= reglasRepetidas(derivacion(r))
    dk,r1,r2 = reglaDK(rules)
    if not (dk):
        sys.exit( "La gramatica no cumple la regla DK por conflicto con las siguientes reglas en el mismo estado:"+str(r1)+str(r2))
    
    else:
        for regla in rules:
            if not(esFinal(regla)):   
                reglaAux  = regla[:]
                reglaAux[2]= reglaAux[2]+1
                if not(reglaAux in rules):
                    newid = i+1
                    transiciones.update( {regla[1][regla[2]] : newid} )
                    e,i=nuevoEstado(reglaAux,newid)
                else:
                    transiciones.update( {regla[1][regla[2]] : idE} )
                    e=[]
                    #Basicamente crear la transicion a si mismo,
            else:
                #Si es terminal, debe crearse el estado 
                e = [i,rules,{},True]
                estados.append(e)
                return estados,i
            estados=estados+e
        estados.append([idE,rules,transiciones,False])
        return estados,i

#Funcion que construye la tabla LR0 a partir del automata
def construyeTabla(aut):
    t=[]
    nt=[]
    for r in reglas:
        for ch in r[1]:
            if not(esNoTerminal(ch) or ch in t):
                t.append(ch)
            elif esNoTerminal(ch) and not( ch in nt):
                nt.append(ch)
    t.sort()      
    len_terminales=len(t)   
    terminales=t[:]  
    t.append("FDC")
    t=t+nt

    tablaLR0 = [["" for x in range(len(t))] for y in range(len(aut))] #Creamos la tabla LR0 vacia
    
    for estado in aut:
        if not(estado[3]): #Es decir, si el estado es no terminal
            for transicion in estado[2]:
                if esNoTerminal(transicion):
                    tablaLR0[estado[0]-1][t.index(transicion)] = estado[2][transicion]
                else:
                    tablaLR0[estado[0]-1][t.index(transicion)] = ("d"+str(estado[2][transicion]))
        else:
            if(estado[1][0][0]=="$"):
                tablaLR0[estado[0]-1][t.index("FDC")]="aceptar"
            elif (estado[1][0][0]=="S"):
                tablaLR0[estado[0]-1][t.index("FDC")]=str(estado[1][0][0])+"->"+str(estado[1][0][1])
            else:
                  for celda in terminales:
                      tablaLR0[estado[0]-1][t.index(celda)]=str(estado[1][0][0])+"->"+str(estado[1][0][1]) 
    if reglaSaLambda==1:
        tablaLR0[0][t.index("FDC")]="aceptar"
    return(tablaLR0,t)
    
    
#------------------------------------------------
#Ejecucion del programa 

automata =nuevoEstado(reglas[-1],1)[0]
automata.sort(key=lambda x: x[0])
lr0,encabezado=construyeTabla(automata)

#Impresion bonita de la tabla:
t = PrettyTable(encabezado)
for row in lr0:
    t.add_row(row)
print(t)


#------------------------------------------------
#Lectura de una cadena segun algoritmo de Brookshear p. 128
cadena = sys.argv[2]
#cadena="zazabzbz"
stack=[]

simboloEspecial=1
stack.append(simboloEspecial)
simbolo=cadena[0]
cadena=cadena[1:]
valorTabla = lr0[simboloEspecial-1][encabezado.index(simbolo)]
while valorTabla != "aceptar":
    if "d" in valorTabla:
        stack.append(simbolo)
        simboloEspecial=(int)(valorTabla.replace("d",""))
        stack.append(simboloEspecial)
        if len(cadena)==0:
            simbolo = "FDC"
        else:
            simbolo=cadena[0]
            cadena=cadena[1:]
    elif "->" in valorTabla:
        for char in  valorTabla.split('->')[1]:    
            stack.pop()
            stack.pop()
        simboloEspecial=(int)(stack[-1])
        stack.append(valorTabla.split('->')[0])
        simboloEspecial=(int)(lr0[simboloEspecial-1][encabezado.index(valorTabla.split('->')[0])])
        stack.append(simboloEspecial)
    else:
        sys.exit("La gramatica no puede procesar la cadena")
    valorTabla=lr0[simboloEspecial-1][encabezado.index(simbolo)]
if simbolo != "FDC":
    sys.exit("La cadena no es aceptada por la gramatica")
else:
    print("La cadena es ACEPTADA por la gramatica")

