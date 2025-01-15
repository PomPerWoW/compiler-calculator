import ply.lex as lex
from src.symbol_table.symbol_table import SymbolTable


class LexicalAnalyzer:
    tokens = (
        "INT",
        "REAL",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "INTEGER_DIVISION",
        "POW",
        "ASSIGNMENT",
        "GREATER_THAN",
        "GREATER_THAN_OR_EQUAL",
        "LESS_THAN",
        "LESS_THAN_OR_EQUAL",
        "EQUAL_TO",
        "NOT_EQUAL",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "VAR",
        "LIST",
        "ERR",
    )

    t_PLUS = r"\+"
    t_MINUS = r"\-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_INTEGER_DIVISION = r"//"
    t_POW = r"\^"
    t_ASSIGNMENT = r"\="
    t_GREATER_THAN = r"\>"
    t_GREATER_THAN_OR_EQUAL = r"\>="
    t_LESS_THAN = r"\<"
    t_LESS_THAN_OR_EQUAL = r"\<="
    t_EQUAL_TO = r"\=="
    t_NOT_EQUAL = r"\!="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"

    t_ignore = " \t"

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_line = 1
        self.build()

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_REAL(self, t):
        r"(0|[1-9][0-9]*)?\.([0-9]+)?([Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+"
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r"(0|[1-9][0-9]*)"
        t.value = int(t.value)
        return t

    def t_LIST(self, t):
        r"list"
        return t

    def t_VAR(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        return t

    def t_ERR(self, t):
        r"[^a-zA-Z0-9\+\-\*\/\^\=\!\(\)\[\]\s\.]+"
        return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

    def tokenize(self, expression):
        self.lexer.input(expression)
        tokens = []

        while True:
            tok = self.lexer.token()
            if not tok:
                break

            # print(
            #     f"Token Type: {tok.type}, Token Value: {tok.value}, Token Line: {tok.lineno}, Token Position: {tok.lexpos}"
            # )

            if tok.type in ("VAR", "LIST"):
                self.symbol_table.insert(
                    lexeme=str(tok.value),
                    line_number=tok.lineno,
                    position=tok.lexpos,
                    token_type=tok.type,
                    value=tok.value,
                )

            tokens.append(f"{tok.value}/{tok.type}")

        return tokens

    def save_symbol_table(self, filename):
        self.symbol_table.save_to_csv(filename)
