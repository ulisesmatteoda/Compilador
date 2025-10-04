from Lexico import Lexico

class Sintactico(Parser):
    tokens = Lexico.tokens

    #Basicamente cual toma primero, va de menor a mayor prioridad. Tambien define asociatividad (left, right,nonassoc)(agrupa primero en alguna direccion)
    precedence =(('nonassoc', 'LE', 'LT', 'GE', 'GT', 'NE', 'IGUAL') #nonassoc, no permite asociatividad sin parentesis, util en comparaciones para que no se haga algo asi: a < b <= c 
                ,('left', '+', '-') #menos prioridad
                ,('left', '*', '/') #mas prioridad
                ,('right', 'UMINUS')) # usa UMINUS, con mas prioridad, para diferenciar el "-", numero negativo, de la resta
    
    def __init__(self): #estructura de apoyo para variables
        self.names = { }

    #PROGRAMA GENERAL
    @_('ID "{" statements "}"')
    def program(self, p):
        print( "ID: " , p.ID,  ", Statements: " , p.statements)
        #return ('program', p.ID, p.statements) #esto decia gpt
    
    @_('statements statement') #Para que pueda tener muchas sentencias, sino solamente podria tener una
    def statements(self, p):
        return p.statements + [p.statement]

    @_('statement')
    def statements(self, p):
        return [p.statement]
    
    @_('sentencia_declarativa') #a chequear si esta bien poner el ";" en esta regla, puede colisionar con otra regla. Todas las sentencias deben terminar con ";" 
    def statements(self, p):
        return p.sentencia_declarativa

    @_('sentencia_ejecutable') #a chequear si esta bien poner el ";" en esta regla, puede colisionar con otra regla. Todas las sentencias deben terminar con ";"
    def statements(self, p):
        return p.sentencia_ejecutable

    @_('expr ;') #Cada sentencia tiene que terminar con ";"
    def statement(self, p):
        return p.expr

    @_('ID')
    def expr(self, p):
        return p.ID

    @_('STRING')
    def expr(self, p):
        return p.STRING
    
    @_('ENTERO')
    def expr(self, p):
        return int(p.ENTERO) #convierte el string a entero


    #Declaracion de UINT
    @_('UINT listaIDs ";" ')
    def sentencia_declarativa(self, p):
        return ('decl', p.UINT, p.listaIDs)
    
    @_('ID')
    def listaIDs(self, p):
        return [p.ID]

    @_('listaIDs "," ID')
    def listaIDs(self, p):
        return p.listaIDs + [p.ID] #de esta forma se hace recursivo y puede haber varios ID separados por ","
    

    #Declaracion de funciones 
    @_('UINT ID "(" parametros_formales ")" "{" statements "}"')
    def sentencia_declarativa(self, p):
        return ('decl', p.UINT, p.ID, p.parametros_formales, p.statements)

    @_('parametro_formal')
    def parametros_formales(self, p):
        return [p.parametro_formal]

    @_('parametros_formales "," parametro_formal')
    def parametros_formales(self, p):
        return p.parametros_formales + [p.parametro_formal]

    @_('sem_pasaje TYPE ID') #sem_pasaje se define en los temas 24-26
    def parametro_formal(self, p):
        return (p.sem_pasaje, p.TYPE, p.ID)
    
    @_('RETURN expr ";"')
    def statement(self, p):
        return ('return', p.expr)

    """
    idea para entender como funcionan las reglas
    <parámetros_formales> ::= <parámetro_formal> | <parámetros_formales> "," <parámetro_formal>
    <parámetro_formal> ::= <sem_pasaje> <tipo> ID
    """


    #Asignaciones
    @_('ID ASIGNACION1 expr') #en asignaciones dice que puede ser operaciones aritmeticas, nosotros lo hicimos para que tambien puedan ser solo numeros, o llamados a funciones, etc
    def sentencia_ejecutable(self, p):
        self.names[p.NAME] = p.expr

    @_('ID ASIGNACION2 expr')
    def sentencia_ejecutable(self, p):
        self.names[p.NAME] = p.expr

    
    #Invocacion a funcion
    @_('ID "(" parametros_reales ")" ')
    def sentencia_ejecutable(self, p): # Esta es para cuando se llama sola en una linea, no por el valor que devuelve sino por sus efectos
        return ('ejec_statement', p.ID, p.parametros_reales)
    
    @_('ID "(" parametros_reales ")" ') #y esta para que pueda llamarse en asignaciones,parametros, etc, cuando devuelve un valor
    def expr(self, p):
        return ('ejec_expr', p.ID, p.parametros_reales)
    
    @_('expr FLECHA parametro_formal')
    def parametro_real(self, p):
        return (p.expr, p.parametro_formal)
    
    @_('parametro_real')
    def parametros_reales(self, p): #en el caso de que solo tenga un parametro
        return [p.parametro_real]
    
    @_('parametros_reales "," parametro_real')
    def parametros_reales(self, p):
        return p.parametros_reales + [p.parametro_real] 
    

    #Clausula IF
    @_('IF "(" condicion ")" bloque_sent_ejec ELSE bloque_sent_ejec ENDIF ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec', p.IF, p.condicion, p.bloque_sent_ejec0, p.bloque_sent_ejec1 , p.ELSE, p.ENDIF)
    
    @_('IF "(" condicion ")" bloque_sent_ejec ENDIF ";"') #sin else
    def sentencia_ejecutable(self, p):
        return ('ejec', p.IF, p.condicion, p.bloque_sent_ejec, p.ELSE, p.ENDIF)
    
    @_('"(" comparacion ")"')
    def condicion(self, p):
        return (p.comparacion)
    
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


    #Sentencia Print
    @_('PRINT "(" ' " ' STRING ' " ' ")" ";"') #le volvemos a poner las comillas que le sacamos en el lexer (a chequear si se puede fixear despues)
    def sentencia_ejecutable(self, p):
        return ('ejec', p.PRINT, p.STRING)
    
    @_('PRINT "(" expr ")" ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec', p.PRINT, p.STRING)
    

    #Sentencia do while
    @_('DO bloque_sent_ejec WHILE condicion')
    def sentencia_ejecutable(self, p):
        return ('ejec', p.DO, p.bloque_sent_ejec, p.WHILE, p.condicion)
    

    #Asignaciones multiples
    @_('lista_variables ASIGNACION1 lista_elementos ";"')
    def sentencia_ejecutable(self, p):
        if len(p.lista_elementos) < len(p.lista_variables): #chequeo semantico
            raise Exception(f"Error semántico: se esperan al menos      {len(p.lista_variables)} valores, "
                            f"pero solo hay {len(p.lista_elementos)}")
        return ('ejec', p.lista_variables, p.ASIGNACION1, p.lista_elementos)
    
    @_('ID')
    def lista_variables(self, p):
        return [p.ID]

    @_('lista_variables "," ID')
    def lista_variables(self, p):
        return p.lista_variables + [p.ID]

    @_('UINT') #las expresiones del lado derecho solo pueden ser constantes
    def lista_expresiones(self, p):
        return [p.UINT]

    @_('lista_expresiones "," UINT')
    def lista_expresiones(self, p):
        return p.lista_expresiones + [p.UINT]


    #Prefijado Obligatorio
    



    #Aritmetica:
    @_('expr "+" expr') 
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('"-" expr %prec UMINUS') #%prec indica que siga la prioridad de UMINUS y no la de '-'
    def expr(self, p):
        return -p.expr


    #Comparadores:
    @_('expr LT expr')
    def comparacion(self, p):
        return p.expr0 < p.expr1

    @_('expr LE expr')
    def comparacion(self, p):
        return p.expr0 <= p.expr1

    @_('expr GT expr')
    def comparacion(self, p):
        return p.expr0 > p.expr1

    @_('expr GE expr')
    def comparacion(self, p):
        return p.expr0 >= p.expr1

    @_('expr EQ expr')
    def comparacion(self, p):
        return p.expr0 == p.expr1

    @_('expr NE expr')
    def comparacion(self, p):
        return p.expr0 != p.expr1
    
    """
    #En asignaciones no se permite expresiones con parentesis, si lo necesito
    para otro caso, o se pueden poner los parentesis en la expresion regular, 
    o se puede separar las expresiones en expr_simple y expr_general, donde una 
    incluya el parentesis y otra no
    @_('"(" expr ")"') 
    def expr(self, p):
        return p.expr
    """
        
    @_('"{" expr "}"') 
    def expr(self, p):
        return p.expr
    



    #Manejo de errores:
    def error(self, p):
        if p:
            print(f"Syntax error at token {p.type}, value {p.value}")
        else:
            print("Syntax error at EOF")
