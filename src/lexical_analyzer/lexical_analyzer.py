import ply.lex as lex


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
    t_EQUAL_TO = r"\=="
    t_NOT_EQUAL = r"\!="
    t_GREATER_THAN = r"\>"
    t_GREATER_THAN_OR_EQUAL = r"\>="
    t_LESS_THAN = r"\<"
    t_LESS_THAN_OR_EQUAL = r"\<="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"

    t_ignore = " \t"

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
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
        t.value = "list"
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

    def _handle_variable_assignment(self, tok, current_var, value):
        self.symbol_table.insert(
            lexeme=current_var,
            line_number=tok.lineno,
            position=tok.lexpos,
            token_type="VAR",
            value=value,
        )

    def _handle_list_declaration(self, tok, current_var, list_size):
        self.symbol_table.insert(
            lexeme=current_var,
            line_number=tok.lineno,
            position=tok.lexpos,
            token_type="LIST",
            value=[0] * list_size,
        )

    def tokenize(self, expression, line_number):
        self.lexer.input(expression)
        self.lexer.lineno = line_number
        tokens = []

        current_var = None
        is_list_declaration = False
        list_size = None
        is_assignment = False
        has_value = False
        value = None
        is_list_access = False

        while True:
            tok = self.lexer.token()
            if not tok:
                break

            match tok.type:
                case "VAR":
                    if not is_list_declaration:
                        current_var = tok.value
                case "ASSIGNMENT":
                    is_assignment = True
                case "LIST":
                    if is_assignment:
                        is_list_declaration = True
                    else:
                        current_var = None
                case "INT":
                    if is_list_declaration:
                        list_size = tok.value
                    elif is_assignment and not is_list_access:
                        has_value = True
                        value = tok.value
                case "REAL":
                    if is_assignment:
                        has_value = True
                        value = tok.value
                case "LBRACKET":
                    is_list_access = True
                case "RBRACKET":
                    if is_list_declaration and current_var and list_size is not None:
                        self._handle_list_declaration(tok, current_var, list_size)
                        current_var = None
                        is_list_declaration = False
                        list_size = None
                        is_assignment = False
                        has_value = False
                        value = None
                        is_list_access = False

            if (
                not is_list_declaration
                and current_var
                and is_assignment
                and has_value
                and is_list_access
            ):
                self._handle_variable_assignment(tok, current_var, value)
                current_var = None
                is_assignment = False
                has_value = False
                value = None
                is_list_access = False

            tokens.append(f"{tok.value}/{tok.type}")

        return tokens

    def save_symbol_table(self, filename):
        self.symbol_table.save_to_csv(filename)
