import ply.yacc as yacc
from src.lexical_analyzer.lexical_analyzer import LexicalAnalyzer


class SyntaxAnalyzer:
    def __init__(self):
        self.lexer = LexicalAnalyzer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)
        self.ast_output = []
        self.symbol_table = {}  # Track defined variables

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
        if p[1] not in self.symbol_table and not isinstance(
            p.parser.lexer, LexicalAnalyzer
        ):
            raise SyntaxError(
                f"Undefined variable {p[1]} at line {p.lineno(1)}, pos {p.lexpos(1)}"
            )
        p[0] = p[1]

    def p_factor_list(self, p):
        """factor : LIST LBRACKET expression RBRACKET"""
        p[0] = ("list", p[3])

    def p_factor_expr(self, p):
        """factor : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_assignment(self, p):
        """expression : VAR ASSIGNMENT expression"""
        self.symbol_table[p[1]] = True  # Mark variable as defined
        p[0] = ("=", p[1], p[3])

    def p_error(self, p):
        if p:
            self.ast_output.append(f"SyntaxError at line {p.lineno}, pos {p.lexpos}")
        else:
            self.ast_output.append("Syntax error at EOF")

    def parse(self, input_text, lineno=1):
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
            self.ast_output.append(f"Error at line {lineno}: {str(e)}")
            return None

    def _format_ast(self, ast):
        """Format AST for output"""
        if isinstance(ast, (int, float)):
            return str(ast)
        elif isinstance(ast, str):
            return ast
        elif isinstance(ast, tuple):
            if ast[0] == "=":
                return f"({ast[1]}={self._format_ast(ast[2])})"
            elif ast[0] == "list":
                return f"(list[{self._format_ast(ast[1])}])"
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
