from sly import Lexer

class Lexico(Lexer):
    # Nombre de los tokens.
    tokens = {ASIGNACION1, ASIGNACION2, FLECHA, LE, LT, GE, GT, NE
            , EQ, IF, ELSE, ENDIF, DO, WHILE, RETURN
            , PRINT, CVR, UINT, STRING, ID, NUMERO}
    
    #literales
    literals = { '(', ')', '{', '}', ';' , '_', ',', '+', '-', '*', '/', '"', "."}

    #caracteres a ignorar
    ignore = ' \t'

    #Comentarios
    @_(r'##[\s\S]*?##')  # [\s\S] = coincide con cualquier carácter, incluyendo saltos de línea.
    def ignore_comment(self, t): 
        pass
    
    #reglas para tokens
    EQ = r'==' #tiene que ir antes del '=' asi lo toma primero
    ASIGNACION1 = r'=' 
    ASIGNACION2= r':='
    FLECHA = r'->'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    NE = r'!='
    IF= r'if'
    ELSE = r'else'
    ENDIF = r'endif'
    DO = r'do'
    WHILE = r'while'
    RETURN = r'return'
    PRINT = r'print'
    CVR = r'cvr' #copia-valor-resultado
    UINT = r'uint' # type, para definir el tipo
    STRING = r'"[^"\n]*"'

    # Identificador: primera letra mayúscula, resto letras mayúsculas, dígitos o %
    @_(r'[A-Z][A-Z0-9%]*')
    def ID(self, t):
        if len(t.value) > 20:
            print(f"Warning: identificador '{t.value}' truncado a 20 caracteres en linea {t.lineno} ")
            t.value = t.value[:20]  # truncar
        return t

# Como el string no se usa en funciones, asignaciones etc, SOLAMENTE en el print, no le sacamos las comillas dobles por ahora asi no se la tenemos que agregar en el parser para imprimirlo
#    @_(r'"[^"\n]*"')
#    def STRING(self, t):
#        # Quitamos las comillas del valor
#        t.value = t.value[1:-1]
#        return t
    
    @_(r'\d+UI')
    def NUMERO(self, t): #teoricamente son constantes
        valor = int(t.value[:-2]) #Quitar el sufijo 'UI'
        if valor < 0 or valor > 65535:
            print(f"Error: valor {valor} fuera del rango de 16 bits en línea {t.lineno}")
        t.value = valor
        return t
    
    
#    Para el TP2 hay que eliminarlo
#    @_(r'(\d+\.\d*|\.\d+)(D[+-]?\d+)?')
#    def DFLOAT(self, t):
#        try:
#            # Reemplazamos 'D' por 'e' para convertir a float de Python
#            value = float(t.value.replace('D', 'e'))
#            # Rango de double en IEEE 754
#            if abs(value) < 2.2250738585072014e-308:
#                print(f"Valor {value} demasiado pequeño para float64")
#            elif abs(value) > 1.7976931348623157e+308:
#                print(f"Valor {value} demasiado grande para float64")
#        except ValueError:
#            print(f"Valor inválido: {t.value}")
#        return t
    
    
    @_(r'\n+') #Lleva la cuenta de que linea estamos
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        # t.value[0] es el carácter problemático, t.index es el desplazamiento
        print(f"[Lex] Carácter ilegal {t.value[0]!r} en línea {self.lineno}, índice {self.index}")
        self.index += 1  # importante: avanzar para no entrar en bucle