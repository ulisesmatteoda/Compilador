from sly import Lexer

class Lexico(Lexer):

    # Nombre de los tokens.

    tokens = {SUMA, RESTA, MULTIPLICACION, DIVISION, ASIGNACION1,
            ASIGNACION2, LE, GE, LT, GT, NE, IGUAL, ID, IF, ELSE, ENDIF, PRINT, RETURN, 
            UINT, DFLOAT, DO, WHILE}

