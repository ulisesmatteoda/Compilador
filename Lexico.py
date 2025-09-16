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
    




