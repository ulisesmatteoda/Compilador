from sly import Lexer

class Lexico(Lexer):

    # Nombre de los tokens.

    tokens = {SUMA, RESTA, MULTIPLICACION, DIVISION, ASIGNACION1,
            ASIGNACION2, LE, GE, LT, GT, NE, IGUAL, ID, IF, ELSE, ENTERO, ENDIF, PRINT, RETURN, 
            UINT, FLECHA, DO, WHILE}
    
    #literales

    literals = { '(', ')', '{', '}', ';' , '_', ',' }

    #caracteres a ignorar

    ignore = ' \t'

    @_((r'##[\s\S]*?##'))
    def ignore_comment(self, t):
        # [\s\S] = coincide con cualquier carácter, incluyendo saltos de línea.
        pass
    
    #reglas para tokens

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
    UINT = r'uint'
    IF= r'if'
    ELSE = r'else'
    ENDIF = r'endif'
    PRINT = r'print'
    RETURN = r'return'
    DO = r'do'
    WHILE = r'while'


    # Identificador: primera letra mayúscula, resto letras mayúsculas, dígitos o %
    @_(r'[A-Z][A-Z0-9%]*')
    def ID(self, t):
        if len(t.value) > 20:
            print(f"Warning: identificador '{t.value}' truncado a 20 caracteres en linea {t.lineno} ")
            t.value = t.value[:20]  # truncar
        return t
    
    

    #UINT
    @_(r'\d+UI')
    def ENTERO(self, t):
        # Quitar el sufijo 'UI'
        valor = int(t.value[:-2])
        if valor < 0 or valor > 65535:
            print(f"Error: valor {valor} fuera del rango de 16 bits en línea {t.lineno}")
        t.value = valor
        return t
    
    #@_(r'(\d+\.\d*|\.\d+)(D[+-]?\d+)?')
    #def DFLOAT(self, t):
    #    try:
            # Reemplazamos 'D' por 'e' para convertir a float de Python
     #       value = float(t.value.replace('D', 'e'))
            # Rango de double en IEEE 754
      #      if abs(value) < 2.2250738585072014e-308:
       #         print(f"Valor {value} demasiado pequeño para float64")
        #    elif abs(value) > 1.7976931348623157e+308:
         #       print(f"Valor {value} demasiado grande para float64")
        #except ValueError:
         #   print(f"Valor inválido: {t.value}")
        #return t

            #Lleva la cuenta de que linea estamos
    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')



if __name__ == '__main__':
    data = ''' 20UI + 3UI 


                X = 3UI 
                
                40UI/3UI+5UI*8UI-5UI
                
                if ID=8UI
                ## HOLA 
                ESTO SE IGNORA
                ##
            
                HOLASOYUNIDENTIFICADORRELARGO = 20UI '''
    lexer = Lexico()
    for tok in lexer.tokenize(data):
        print(tok)



