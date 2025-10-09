from sly import Parser
from Lexico import Lexico

class Sintactico(Parser):
    tokens = Lexico.tokens
    debugfile = 'parser.out'   

    #Basicamente cual toma primero, va de menor a mayor prioridad. Tambien define asociatividad (left, right,nonassoc)(agrupa primero en alguna direccion)
    precedence =(('nonassoc', 'LE', 'LT', 'GE', 'GT', 'NE', 'EQ') #nonassoc, no permite asociatividad sin parentesis, util en comparaciones para que no se haga algo asi: a < b <= c 
                ,('left', '+', '-') #menos prioridad
                ,('left', '*', '/') #mas prioridad
                ,('right', 'UMINUS')) # usa UMINUS, con mas prioridad, para diferenciar el "-", numero negativo, de la resta

    #PROGRAMA GENERAL
    @_('ID "{" statements "}"')
    def program(self, p):
        return ('program', p.ID, p.statements)
    
    @_('statements statement') #Para que pueda tener muchas sentencias, sino solamente podria tener una
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]
    
    @_('sentencia_declarativa')  
    def statement(self, p):
        return p.sentencia_declarativa

    @_('sentencia_ejecutable') 
    def statement(self, p):
        return p.sentencia_ejecutable

    #Simbolos terminales: van a ->expr o ->statement
    @_('ID opt_prefijo') #Prefijado Obligatorio
    def variable(self,p):
        return (p.ID, p.opt_prefijo)

    @_('"." ID')
    def opt_prefijo(self,p): 
        return p.ID

    @_('')
    def opt_prefijo(self,p): 
        return '' #devuelvo esto asi es mas facil leerlo en la salida de la consola
    
    @_('atom_expr') #atomizamos expr, asi no transforma las reglas de forma inmediata
    def expr(self, p): 
        return p.atom_expr

    @_('variable')
    def atom_expr(self, p):
        return p.variable

    @_('STRING')
    def atom_expr(self, p):
        return p.STRING
    
    @_('NUMERO')
    def atom_expr(self, p):
        return int(p.NUMERO) #convierte el string a entero
    
    #Agrupacion de <tipo> <variable>
    @_('UINT ID')
    def uint_id(self, p): #cabezera de declaracion, se usa en declaraciones de funciones, y expresiones lambda. Asi se evitan shitf-reduce
        return (p.UINT, p.ID)

    @_('UINT lista_variables') #se usa en declaracion simple, lista de variables separadas por ","
    def uint_variables(self, p): #mantenerlo de uint_id en reglas disjuntas,sino hay conflicto
        return (p.UINT, p.lista_variables) 


    #Declaracion de UINT
    @_('uint_variables ";" ')
    def sentencia_declarativa(self, p):
        return ('decl_uint', p.uint_variables)
    
    @_('variable')
    def lista_variables(self, p):
        return [p.variable]

    @_('lista_variables "," variable') 
    def lista_variables(self, p):
        return p.lista_variables + [p.variable]
    

    #Declaracion de funciones 
    @_('uint_id "(" parametros_formales ")" "{" statements "}" ";" ')
    def sentencia_declarativa(self, p):
        return ('decl_func', p.uint_id, p.parametros_formales, p.statements)

    @_('parametro_formal')
    def parametros_formales(self, p):
        return [p.parametro_formal]

    @_('parametros_formales "," parametro_formal')
    def parametros_formales(self, p):
        return p.parametros_formales + [p.parametro_formal]
    
    @_('CVR UINT variable') 
    def parametro_formal(self, p): #copia-valor-resultado, TEMA 26
        return (p.CVR, p.UINT, p.variable)

    @_('UINT variable') 
    def parametro_formal(self, p):
        return (p.UINT, p.variable)
    
    @_('RETURN "(" expr ")" ";"') #el return tiene que estar entre parentesis si o si
    def sentencia_ejecutable(self, p):
        return ('return', p.expr)
    

    #Asignaciones
    @_('variable ASIGNACION2 expr ";"') # vamos a usar ASIGNACION1 para asignaciones multiples, y ASIGNACION2 para asignaciones normales
    def sentencia_ejecutable(self, p):
        return ('ejec_asign', p.variable, p.ASIGNACION2, p.expr)
    
    #Asignaciones multiples
    @_('lista_variables ASIGNACION1 lista_elementos ";"')
    def sentencia_ejecutable(self, p):
        if len(p.lista_elementos) < len(p.lista_variables): #chequeo semantico
            raise Exception(f"Error semántico: se esperan al menos      {len(p.lista_variables)} valores, "
                            f"pero solo hay {len(p.lista_elementos)}")
        return ('ejec_asign_mult', p.lista_variables, p.ASIGNACION1, p.lista_elementos)

    @_('NUMERO') #las expresiones del lado derecho solo pueden ser constantes
    def lista_elementos(self, p):
        return [int(p.NUMERO)]

    @_('lista_elementos "," NUMERO')
    def lista_elementos(self, p):
        return p.lista_elementos + [int(p.NUMERO)]

    
    #Invocacion a funcion
    @_('ID "(" parametros_reales ")"')
    def atom_expr(self, p): 
        return ('ejec_llamada_funcion', p.ID, p.parametros_reales)

    @_('expr FLECHA variable')
    def parametro_real(self, p):
        return (p.expr, p.variable)
    
    @_('parametro_real')
    def parametros_reales(self, p): #en el caso de que solo tenga un parametro
        return [p.parametro_real]
    
    @_('parametros_reales "," parametro_real')
    def parametros_reales(self, p):
        return p.parametros_reales + [p.parametro_real] 
    

    #Clausula IF
    @_('IF "(" comparacion ")" bloque_sent_ejec opt_else ENDIF ";"') #el else es opcional, asi no hay shift-reduce
    def sentencia_ejecutable(self, p):
        return ('ejec_if', p.comparacion, p.bloque_sent_ejec, p.opt_else)

    @_('ELSE bloque_sent_ejec')
    def opt_else(self, p):
        return ('else', p.bloque_sent_ejec)

    @_('')
    def opt_else(self, p):
        return 'No else'
    
    @_('sentencia_ejecutable')
    def bloque_sent_ejec(self, p): #una sola sin "{}"
        return p.sentencia_ejecutable

    @_('sentencia_ejecutable')
    def lista_sent_ejec(self, p): 
        return [p.sentencia_ejecutable]
    
    @_('lista_sent_ejec sentencia_ejecutable')
    def lista_sent_ejec(self, p):
        return p.lista_sent_ejec + [p.sentencia_ejecutable]
    
    @_('"{" lista_sent_ejec "}"')
    def bloque_sent_ejec(self, p):
        return p.lista_sent_ejec


    #Sentencia do while
    @_('DO bloque_sent_ejec WHILE "(" comparacion ")" ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec_while', p.DO, p.bloque_sent_ejec, p.WHILE, p.comparacion)
    

    #Sentencia Print    
    @_('PRINT "(" expr ")" ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec_print', p.expr)


    #Expresiones lambda: En linea
    @_('"(" uint_id ")" bloque_sent_ejec "(" argumento ")" ";"') #son statement, ya que solo se pueden usar en una linea, sino serian expr y se podrian usar en todas partes
    def sentencia_ejecutable(self, p ):
        return ('Expresion lambda', p.uint_id, p.bloque_sent_ejec, p.argumento)

    @_('variable')
    def argumento(self, p):
        return p.variable

    @_('NUMERO')
    def argumento(self, p):
        return int(p.NUMERO)
    

    #Conversiones: implicitas
    #no hay que hacer nada, se explica en los tp 3 y 4


    #Aritmetica:
    @_('expr "+" expr')
    def atom_expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def atom_expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def atom_expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def atom_expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS') #%prec indica que siga la prioridad de UMINUS y no la de '-'
    def atom_expr(self, p):
        return ('uminus', p.expr)


    #Comparadores:
    @_('expr LT expr')
    def comparacion(self, p):
        return ('lt', p.expr0, p.expr1)

    @_('expr LE expr')
    def comparacion(self, p):
        return ('le', p.expr0, p.expr1)

    @_('expr GT expr')
    def comparacion(self, p):
        return ('gt', p.expr0, p.expr1)

    @_('expr GE expr')
    def comparacion(self, p):
        return ('ge', p.expr0, p.expr1)

    @_('expr EQ expr')
    def comparacion(self, p):
        return ('eq', p.expr0, p.expr1)

    @_('expr NE expr')
    def comparacion(self, p):
        return ('ne', p.expr0, p.expr1)
    
    
    # ERRORES PERSONALIZADOS
    #falta nombre del programa o corchetes
    @_('error "{" statements "}" ')
    def program(self, p):
        print(f"Error linea: {p.lineno}: falta el nombre del programa")
        return ('error',)
    
    @_('ID statements "}"')
    def program(self, p):
        print(f"Error linea: {p.lineno}: falta el primer corchete del bloque")
        return ('error',)
    
    @_('ID statements "}"')
    def program(self, p):
        print(f"Error linea: {p.lineno}: falta el segundo corchete del bloque")
        return ('error',)
    
    #falta ";"
    @_('uint_variables error ') #declaracion de variable
    def sentencia_declarativa(self, p):
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)
    
    @_('uint_id "(" parametros_formales ")" "{" statements "}" error ')
    def sentencia_declarativa(self, p): #declaracion de funciones
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)
  
    @_('variable ASIGNACION2 expr error')
    def sentencia_ejecutable(self, p): #asignaciones simples
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)
    
    @_('lista_variables ASIGNACION1 lista_elementos error')
    def sentencia_ejecutable(self, p): #asignaciones multiples
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)

    @_('IF "(" comparacion ")" bloque_sent_ejec opt_else ENDIF error') 
    def sentencia_ejecutable(self, p): #if
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)
    
    @_('DO bloque_sent_ejec WHILE "(" comparacion ")" error')
    def sentencia_ejecutable(self, p): #do while
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)

    @_('PRINT "(" expr ")" error')
    def sentencia_ejecutable(self, p): #print
        print(f"Error linea: {p.lineno}: falta el ';' al final de la sentencia")
        return ('error',)
    
    @_('error "(" parametros_formales ")" "{" statements "}" ";" ')
    def sentencia_declarativa(self, p):
        print(f"Error linea: {p.lineno}: falta el nombre de la funcion")
        return ('error',)
    
    @_('lista_variables error variable')
    def lista_variables(self, p):
        print(f"Error linea: {p.lineno}: falta ',' antes de {p.variable}") #en declaracion de variables, tambien sirve para asignaciones multiples del lado izquierdo
        return ('error',)
    
    #falta el nombre de parametro formal en declaracion de funcion
    @_('CVR UINT error') 
    def parametro_formal(self, p): 
        print(f"Error linea: {p.lineno}: falta el nombre del parametro formal") 
        return ('error',)

    @_('UINT error') 
    def parametro_formal(self, p):
        print(f"Error linea: {p.lineno}: falta el nombre del parametro formal") 
        return ('error',)
    
    #falta de tipo en parametro formal en declaracion de funcion
    @_('CVR error variable') 
    def parametro_formal(self, p): 
        print(f"Error linea: {p.lineno}: falta el tipo del parametro formal") 
        return ('error',)

    @_('error variable') 
    def parametro_formal(self, p):
        print(f"Error linea: {p.lineno}: falta el tipo del parametro formal") 
        return ('error',)
    
    #falta de parametro formal al que corresponde el parametro real
    @_('expr FLECHA error')
    def parametro_real(self, p):
        print(f"Error linea: {p.lineno}: falta el parametro formal al que apunta {p.expr}") 
        return ('error',)
    
    #falta argumento en sentencia print
    @_('PRINT "(" error ")" ";"')
    def sentencia_ejecutable(self, p):
        print(f"Error linea: {p.lineno}: falta el argumento a imprimir") 
        return ('error',)
    
    #falta parentesis de apertura o cierre en if o do while
    @_('error lista_sent_ejec "}"')
    def bloque_sent_ejec(self, p):
        print(f"Error linea: {p.lineno}: falta el parentesis de apertura") 
        return ('error',)

    @_('"{" lista_sent_ejec error')
    def bloque_sent_ejec(self, p):
        print(f"Error linea: {p.lineno}: falta el parentesis de cierre") 
        return ('error',)

    #falta cuerpo en iteraciones
    @_('DO error WHILE "(" comparacion ")" ";"')
    def sentencia_ejecutable(self, p):    
        print(f"Error linea: {p.lineno}: falta el cuerpo del 'do'") 
        return ('error',)
    
    #falta de endif
    @_('IF "(" comparacion ")" bloque_sent_ejec opt_else error ";"')
    def sentencia_ejecutable(self, p):
        print(f"Error linea: {p.lineno}: falta el endif'") 
        return ('error',)

    #Falta de contenido en bloque then-else
    @_('IF "(" comparacion ")" error opt_else ENDIF ";"') 
    def sentencia_ejecutable(self, p):
        print(f"Error linea: {p.lineno}: falta el bloque del 'if''") 
        return ('error',)

    @_('ELSE error')
    def opt_else(self, p):
        print(f"Error linea: {p.lineno}: falta el bloque del 'else''") 
        return ('error',)
    
    #falta de operando en expresion
    @_('error "+" expr')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la suma con {p.expr}") 
        return ('error',)

    @_('expr "+" error')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la suma con {p.expr}") 
        return ('error',)


    @_('error "-" expr')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la resta con {p.expr}") 
        return ('error',)
    
    @_('expr "-" error')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la resta con {p.expr}") 
        return ('error',)

    @_('error "*" expr')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la multiplicacion con {p.expr}") 
        return ('error',)
    
    @_('expr "*" error')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la multiplicacion con {p.expr}") 
        return ('error',)

    @_('error "/" expr')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la division con {p.expr}") 
        return ('error',)
    
    @_('expr "/" error')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta el operando de la division con {p.expr}") 
        return ('error',)

    #falta de operador en expresion
    @_('expr error expr')
    def atom_expr(self, p):
        print(f"Error linea: {p.lineno}: falta de operando en expresion") 
        return ('error',)
    
    #falta de comparador en comparacion
    @_('expr error expr')
    def comparacion(self, p):
        print(f"Error linea: {p.lineno}: falta de comparador en comparacion") 
        return ('error',)
    
    #falta while
    @_('DO bloque_sent_ejec error "(" comparacion ")" ";"')
    def sentencia_ejecutable(self, p):
        print(f"Error linea: {p.lineno}: falta while antes de la comparacion") 
        return ('error',)

    #falta de “,” en lista de elementos del lado izquierdo o del lado derecho
    @_('lista_elementos error NUMERO')
    def lista_elementos(self, p): #del lado derecho, del lado izquierdo fue definida mas arriba para declaracion de variables, usan el mismo no terminal
        print(f"Error linea: {p.lineno}: falta ',' antes de {p.NUMERO}") 
        return ('error',)
    
    # Falta de le después de cv o cr / Falta de cr o cv antes de le
    @_('error UINT variable') 
    def parametro_formal(self, p): #copia-valor-resultado, TEMA 26
        print(f"Error linea: {p.lineno}: falta o esta mal escrito la semantica de pasaje de parametros") 
        return ('error',)

    @_('CVR UINT error') 
    def parametro_formal(self, p):
        print(f"Error linea: {p.lineno}: falta una variable en la definicion de los parametros") 
        return ('error',)

    #falta delimitadores en funcion lambda: solucionado, es bloque_sent_ejec, aplica la misma regla para los bloques del if,else, y while


    def error(self, p):
        if p:
            print(f"Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}' de tipo {p.type} en index: {p.index}")
        else:
            print("Error de sintaxis: fin de archivo inesperado")