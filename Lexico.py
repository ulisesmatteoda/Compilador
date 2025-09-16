from sly import Lexer

class Lexico(Lexer):

    # Nombre de los tokens.

    tokens = {SUMA, RESTA, MULTIPLICACION, DIVISION, ASIGNACION1,
            ASIGNACION2, LE, GE, LT, GT, NE, IGUAL, ID, IF, ELSE, ENDIF, PRINT, RETURN, 
            UINT, DFLOAT, DO, WHILE, FLECHA}
    
    #literales

    literals = { '(', ')', '{', '}', ';' }

    #caracteres a ignorar

    ignore = ' \t'

    #reglas para tokens.

    FLECHA = r'->'
    RESTA = r'\-'
    SUMA =  r'\+'
    MULTIPLICACION = r'\*'
    DIVISION = r'/'
    IGUAL = r'=='
    ASIGNACION1 = r'='
    ASIGNACION2= r':='
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    NE = r'!='
    

    # Identificador: primera letra mayúscula, resto letras mayúsculas, dígitos o %
    @_(r'[A-Z][A-Z0-9%]*')
    def ID(self, t):
        if len(t.value) > 20:
            print(f"Warning: identificador '{t.value}' truncado a 20 caracteres en linea {t.lineno} ")
            t.value = t.value[:20]  # truncar
        return t
    
    #Lleva la cuenta de que linea estamos
    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')





