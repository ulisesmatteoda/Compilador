
class Sintactico(Parser):
    tokens = Lexico.tokens

    #Basicamente cual toma primero, va de menor a mayor prioridad. Tambien define asociatividad (left, right,nonassoc)(agrupa primero en alguna direccion)
    precedence =(('nonassoc', 'LE', 'LT', 'GE', 'GT', 'NE', 'IGUAL') #nonassoc, no permite asociatividad sin parentesis, util en comparaciones para que no se haga algo asi: a < b <= c 
                ,('left', '+', '-') #menos prioridad
                ,('left', '*', '/') #mas prioridad
                ,('right', 'UMINUS')) # usa UMINUS, con mas prioridad, para diferenciar el "-", numero negativo, de la resta
    
    def __init__(self): #estructura de apoyo para variables
        self.names = { }

 
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
        return int(p.ENTERO)
    

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
    

    #Asignacion:
    @_('ID "=" expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    @_('ID ":=" expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr


    #Comparadores:
    @_('expr LT expr')
    def expr(self, p):
        return p.expr0 < p.expr1

    @_('expr LE expr')
    def expr(self, p):
        return p.expr0 <= p.expr1

    @_('expr GT expr')
    def expr(self, p):
        return p.expr0 > p.expr1

    @_('expr GE expr')
    def expr(self, p):
        return p.expr0 >= p.expr1

    @_('expr EQ expr')
    def expr(self, p):
        return p.expr0 == p.expr1

    @_('expr NE expr')
    def expr(self, p):
        return p.expr0 != p.expr1
    
    @_('"(" expr ")"') 
    def expr(self, p):
        return p.expr
    
    @_('"{" expr "}"') 
    def expr(self, p):
        return p.expr
    



    #Manejo de errores:
    def error(self, p):
        if p:
            print(f"Syntax error at token {p.type}, value {p.value}")
        else:
            print("Syntax error at EOF")
