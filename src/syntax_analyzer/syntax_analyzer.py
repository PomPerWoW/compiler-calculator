import ply.yacc as yacc
from src.lexical_analyzer.lexical_analyzer import LexicalAnalyzer


class SyntaxAnalyzer:
    def __init__(self, symbol_table, lexical_analyzer):
        self.lexer = lexical_analyzer
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)
        self.ast_output = []
        self.symbol_table = symbol_table

    def p_expression_binary(self, p):
        """
        expression : expression PLUS term
                  | expression MINUS term
                  | expression EQUAL_TO term
                  | expression NOT_EQUAL term
                  | expression GREATER_THAN term
                  | expression GREATER_THAN_OR_EQUAL term
                  | expression LESS_THAN term
                  | expression LESS_THAN_OR_EQUAL term
        """
        p[0] = (p[2], p[1], p[3])

    def p_expression_term(self, p):
        """expression : term"""
        p[0] = p[1]

    def p_term_binary(self, p):
        """
        term : term TIMES factor
             | term DIVIDE factor
             | term INTEGER_DIVISION factor
             | term POW factor
        """
        p[0] = (p[2], p[1], p[3])

    def p_term_factor(self, p):
        """term : factor"""
        p[0] = p[1]

    def p_factor_number(self, p):
        """
        factor : INT
              | REAL
        """
        p[0] = p[1]

    def p_factor_var(self, p):
        """factor : VAR"""
        symbol = self.symbol_table.lookup(p[1])
        if not symbol:
            raise ValueError(f"Undefined variable '{p[1]}' at line {p.lineno(1)}")
        p[0] = symbol.value if symbol.value is not None else p[1]

    def p_factor_list_declaration(self, p):
        """factor : LIST LBRACKET expression RBRACKET"""
        # Validate list size
        if not isinstance(p[3], int) or p[3] <= 0:
            raise ValueError(f"List size must be a positive integer, got {p[3]}")

        # Create list with initial values
        list_value = {
            "type": "list",
            "size": p[3],
            "elements": [0] * p[3],  # Initialize all elements to 0
        }
        p[0] = ("list_decl", p[3], list_value)

    def p_factor_list_access(self, p):
        """factor : VAR LBRACKET expression RBRACKET"""
        # Check if variable exists
        symbol = self.symbol_table.lookup(p[1])
        if not symbol:
            raise ValueError(f"Undefined variable '{p[1]}' at line {p.lineno(1)}")

        # Check if it's a list
        if not isinstance(symbol.value, dict) or symbol.value.get("type") != "list":
            raise ValueError(f"Variable '{p[1]}' is not a list at line {p.lineno(1)}")

        # Validate index
        if not isinstance(p[3], int):
            raise ValueError(f"List index must be an integer, got {p[3]}")

        if p[3] < 0 or p[3] >= symbol.value["size"]:
            raise IndexError(
                f"Index {p[3]} out of range for list '{p[1]}' of size {symbol.value['size']}"
            )

        # Return the list element value
        p[0] = symbol.value["elements"][p[3]]

    def p_assignment_list_element(self, p):
        """expression : VAR LBRACKET expression RBRACKET ASSIGNMENT expression"""
        # Check if variable exists
        symbol = self.symbol_table.lookup(p[1])
        if not symbol:
            raise ValueError(f"Undefined variable '{p[1]}' at line {p.lineno(1)}")

        # Check if it's a list
        if not isinstance(symbol.value, dict) or symbol.value.get("type") != "list":
            raise ValueError(f"Variable '{p[1]}' is not a list at line {p.lineno(1)}")

        # Validate index
        if not isinstance(p[3], int):
            raise ValueError(f"List index must be an integer, got {p[3]}")

        if p[3] < 0 or p[3] >= symbol.value["size"]:
            raise IndexError(
                f"Index {p[3]} out of range for list '{p[1]}' of size {symbol.value['size']}"
            )

        # Validate assigned value is integer
        if not isinstance(p[6], int):
            raise ValueError(f"List elements must be integers, got {p[6]}")

        # Update list element
        symbol.value["elements"][p[3]] = p[6]
        p[0] = ("list_assign", p[1], p[3], p[6])

    def p_factor_expr(self, p):
        """factor : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_assignment(self, p):
        """expression : VAR ASSIGNMENT expression"""
        # For list declaration, handle differently
        if (
            isinstance(p[3], tuple)
            and p[3][0] == "list_decl"
            and isinstance(p[3][2], dict)
        ):
            self.symbol_table.insert(
                lexeme=p[1],
                line_number=p.lineno(1),
                position=p.lexpos(1),
                token_type="VAR",
                value=p[3][2],  # Store the list value dictionary
            )
        else:
            # Regular variable assignment
            value = p[3] if isinstance(p[3], (int, float, str)) else None
            self.symbol_table.insert(
                lexeme=p[1],
                line_number=p.lineno(1),
                position=p.lexpos(1),
                token_type="VAR",
                value=value,
            )
        p[0] = ("=", p[1], p[3])

    def p_error(self, p):
        if p:
            symbol = self.symbol_table.lookup(str(p.value))
            if symbol:
                self.ast_output.append(
                    f"SyntaxError at line {symbol.line_number}, pos {symbol.position}"
                )
            else:
                self.ast_output.append(f"Undefined symbol '{p.value}'")
        else:
            self.ast_output.append("Syntax error at EOF")

    def parse(self, input_text, line_number=1):
        """Parse input text and return the AST"""
        try:
            ast = self.parser.parse(input_text, lexer=self.lexer.lexer)
            if ast:
                self.ast_output.append(self._format_ast(ast))
            return ast
        except SyntaxError as e:
            self.ast_output.append(str(e))
            return None
        except Exception as e:
            self.ast_output.append(f"Error at line {line_number}: {str(e)}")
            return None

    def _format_ast(self, ast):
        """Format AST for output"""
        if isinstance(ast, (int, float)):
            return str(ast)
        elif isinstance(ast, str):
            symbol = self.symbol_table.lookup(ast)
            if symbol and symbol.value is not None:
                return str(symbol.value)
            return ast
        elif isinstance(ast, tuple):
            if ast[0] == "list_decl":
                return f"(list[{ast[1]}])"
            elif ast[0] == "list_access":
                return f"({ast[1]}[{ast[2]}])"
            elif ast[0] == "list_assign":
                return f"({ast[1]}[{ast[2]}]={ast[3]})"
            elif ast[0] == "=":
                return f"({ast[1]}={self._format_ast(ast[2])})"
            else:
                return f"({self._format_ast(ast[1])}{ast[0]}{self._format_ast(ast[2])})"
        return str(ast)

    def save_parsed_output(self, filename):
        """Save the parsed output to a file"""
        with open(filename, "w") as f:
            for output in self.ast_output:
                f.write(f"{output}\n")


# def main():
#     """Test function for the parser"""
#     analyzer = SyntaxAnalyzer()

#     # Test expressions
#     test_expressions = [
#         "23+8",
#         "2.5 * 0",
#         "x = 5",
#         "10 * x",
#         "x = y",
#         "x != 5",
#         "(2 + 5)",
#         "x = list[2]",
#     ]

#     print("Testing parser with expressions:")
#     print("-" * 40)

#     for expr in test_expressions:
#         print(f"\nParsing: {expr}")
#         try:
#             result = analyzer.parse(expr)
#             print(f"Result: {result}")
#         except Exception as e:
#             print(f"Error: {str(e)}")


# if __name__ == "__main__":
#     main()
