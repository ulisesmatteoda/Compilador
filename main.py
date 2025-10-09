from sly import Lexer, Parser
from Lexico import Lexico
from Sintactico import Sintactico

if __name__ == '__main__':
    lexer = Lexico()
    parser = Sintactico()

    with open("test_err2.txt") as f:
        data = f.read()

    # Tokenizar
    print("=== TOKENS ===")
    for tok in lexer.tokenize(data):
        print(tok)

    # Parsear
    print("\n=== AST ===")
    result = parser.parse(lexer.tokenize(data))
    print(result)
