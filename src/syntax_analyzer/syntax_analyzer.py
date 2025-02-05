import ply.yacc as yacc


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
        self._validate_variable(p[1], p.lineno(1), p.lexpos(1))
        p[0] = p[1]

    def p_factor_list_declaration(self, p):
        """factor : LIST LBRACKET expression RBRACKET"""
        if not isinstance(p[3], int) or p[3] <= 0:
            raise ValueError(f"List size must be a positive integer, got {p[3]}")
        p[0] = ("list_decl", p[3])

    def p_factor_list_access(self, p):
        """factor : VAR LBRACKET expression RBRACKET"""
        symbol = self._validate_list_variable(p[1], p.lineno(1), p.lexpos(1))
        self._validate_list_index(
            p[1], p[3], len(symbol.value), p.lineno(1), p.lexpos(1)
        )
        p[0] = (p[1], "[", p[3], "]")

    def p_assignment_list_element(self, p):
        """expression : VAR LBRACKET expression RBRACKET ASSIGNMENT expression"""
        symbol = self._validate_list_variable(p[1], p.lineno(1), p.lexpos(1))
        self._validate_list_index(
            p[1], p[3], len(symbol.value), p.lineno(1), p.lexpos(1)
        )
        value = p[6] if isinstance(p[6], int) else None
        symbol.value[p[3]] = value

        if not isinstance(p[6], int):
            raise ValueError(
                f"List elements must be integers, got {p[6]} at line {p.lineno(1)}, pos {p.lexpos(1) + 1}"
            )

        symbol.value[p[3]] = p[6]
        p[0] = ("list_assign", p[1], p[3], p[6])

    def p_factor_expr(self, p):
        """factor : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_assignment(self, p):
        """expression : VAR ASSIGNMENT expression"""
        if isinstance(p[3], tuple) and p[3][0] == "list_decl":
            list_size = p[3][1]
            self.symbol_table.insert(
                lexeme=p[1],
                line_number=p.lineno(1),
                position=p.lexpos(1),
                token_type="LIST",
                value=[0] * list_size,
            )
        else:
            value = (
                p[3]
                if isinstance(p[3], (int, float))
                else self._evaluate_expression(p[3])
            )
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
            raise SyntaxError((p.value, p.lineno, p.lexpos))
        else:
            raise SyntaxError("EOF")

    def _evaluate_expression(self, expr):
        """Evaluate an expression and return its value"""
        if isinstance(expr, (int, float)):
            return expr
        elif isinstance(expr, str):
            symbol = self.symbol_table.lookup(expr)
            if symbol and symbol.value is not None:
                return symbol.value
            return None
        elif isinstance(expr, tuple):
            if expr[0] == "+":
                return self._evaluate_expression(expr[1]) + self._evaluate_expression(
                    expr[2]
                )
            elif expr[0] == "-":
                return self._evaluate_expression(expr[1]) - self._evaluate_expression(
                    expr[2]
                )
            elif expr[0] == "*":
                return self._evaluate_expression(expr[1]) * self._evaluate_expression(
                    expr[2]
                )
            elif expr[0] == "/":
                return self._evaluate_expression(expr[1]) / self._evaluate_expression(
                    expr[2]
                )
            elif expr[0] == "%":
                return self._evaluate_expression(expr[1]) % self._evaluate_expression(
                    expr[2]
                )
            elif expr[0] == "^":
                return self._evaluate_expression(expr[1]) ** self._evaluate_expression(
                    expr[2]
                )
        return None

    def _validate_variable(self, var_name, lineno, lexpos):
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            raise ValueError(
                f"Undefined variable '{var_name}' at line {lineno}, pos {lexpos + 1}"
            )
        return symbol

    def _validate_list_variable(self, var_name, lineno, lexpos):
        symbol = self._validate_variable(var_name, lineno, lexpos)
        if symbol.token_type != "LIST":
            raise ValueError(
                f"Variable '{var_name}' is not a list at line {lineno}, pos {lexpos + 1}"
            )
        return symbol

    def _validate_list_index(self, list_name, index, size, lineno, lexpos):
        if not isinstance(index, int):
            raise ValueError(
                f"List index must be an integer, got {index} at line {lineno}, pos {lexpos + 1}"
            )
        if index < 0 or index >= size:
            raise ValueError(
                f"Index {index} out of range for list '{list_name}' of size {size} at line {lineno}, pos {lexpos + 1}"
            )

    def _format_ast(self, ast):
        if isinstance(ast, (int, float)):
            return str(ast)
        elif isinstance(ast, str):
            return ast
        elif isinstance(ast, tuple):
            if ast[0] == "list_decl":
                return f"(list[(2)])"
            elif len(ast) == 4 and ast[1] == "[":  # List access operation
                return f"({ast[0]}[({ast[2]})])"  # Added outer parentheses
            elif ast[0] == "list_assign":
                return f"(({ast[1]}[({ast[2]})])={ast[3]})"  # Added extra parentheses
            elif ast[0] == "=":
                return f"({ast[1]}={self._format_ast(ast[2])})"
            else:
                # For binary operations, check if operands are list access and keep their parentheses
                left = self._format_ast(ast[1])
                right = self._format_ast(ast[2])
                return f"({left}{ast[0]}{right})"
        return str(ast)

    def parse(self, input_text):
        try:
            ast = self.parser.parse(input_text, lexer=self.lexer.lexer)
            if ast:
                formatted_ast = self._format_ast(ast)
                self.ast_output.append(formatted_ast)
            return ast
        except ValueError as e:
            self.ast_output.append(str(e))
            return None
        except SyntaxError as e:
            val, line_no, pos = e.args[0]
            self.ast_output.append(f"SyntaxError at line {line_no}, pos {pos + 1}")
            return None
        except Exception as e:
            self.ast_output.append(str(e))
            return None

    def save_parsed_output(self, filename):
        with open(filename, "w") as f:
            for output in self.ast_output:
                f.write(f"{output}\n")
