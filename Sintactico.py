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

    #PROBLEMAS PRINCIPALES:
    # 1) Uso de uint_lista_de_variables y uint_ID, donde solo es una variable. Problema shift-reduce, no sabe
    # cual de los dos elegir, por que arrancan igual, 'UINT variable'
    # 2) Mismo problema con variable y ID, donde capaz dos reglas arrancan con variable o ID, y no sabe cual
    # tomar, por defecto SLY hace shift y pregunta por el simbolo que le sigue, asi elije la regla. Se deberia 
    # arreglar gramaticalmente
    # 3) Ademas de estos shift-reduce, falta probar las estructuras(estos problemas no dejan que funcione) 


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

#    @_('expr ;') #Cada sentencia tiene que terminar con ";"
#    def statement(self, p):
#        return p.expr
    #Prefijado Obligatorio
    @_('ID opt_prefijo')
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
    

    
    @_('UINT ID')
    def uint_id(self, p):#cabezera de declaracion, se usa en declaraciones de funciones, y expresiones lambda. Asi se evitan shitf-reduce
        return (p.UINT, p.ID)

    @_('UINT lista_variables') 
    def uint_variables(self, p): #mantenerlo de uint_id en reglas disjuntas,sino hay conflicto
        return (p.UINT, p.lista_variables) 


    #Declaracion de UINT
    @_('uint_variables ";" ')
    def sentencia_declarativa(self, p):
        return ('decl_uint', p.uint_variables)
    
    @_('variable')
    def lista_variables(self, p):
        return [p.variable]

    @_('lista_variables "," variable') #La lista de variables será una lista de identificadores separados con coma ( “,” ) 
    def lista_variables(self, p):
        return p.lista_variables + [p.variable]
    

    #Declaracion de funciones 
    @_('uint_id "(" parametros_formales ")" "{" statements "}"')
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
        return ('decl_asign', p.variable, p.ASIGNACION2, p.expr)

    
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


    #Sentencia Print    
    @_('PRINT "(" expr ")" ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec_print', p.expr)
    

    #Sentencia do while
    @_('DO bloque_sent_ejec WHILE "(" comparacion ")" ";"')
    def sentencia_ejecutable(self, p):
        return ('ejec_while', p.DO, p.bloque_sent_ejec, p.WHILE, p.comparacion)
    

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


    #Expresiones lambda: En linea
    @_('"(" uint_id ")" bloque_sent_ejec "(" argumento ")"') #son statement, ya que solo se pueden usar en una linea, sino serian expr y se podrian usar en todas partes
    def sentencia_ejecutable(self, p ):
        return ('Expresion lambda', p.uint_id, p.bloque_sent_ejec, p.argumento)

    @_('variable')
    def argumento(self, p):
        return p.variable

    @_('UINT')
    def argumento(self, p):
        return int(p.UINT)
    

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
    
 
     #Ejemplo error personalizado
#    @_('ID ":=" error ";"')
#    def sentencia_ejecutable(self, p):
#        print(f"[Error de asignación] Línea {p.lineno}: "
#            f"expresión inválida en el lado derecho de ':='")
#        return ('error_assign',)

    def error(self, p):
        if p:
            print(f"Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}' de tipo {p.type}")
        else:
            print("Error de sintaxis: fin de archivo inesperado")