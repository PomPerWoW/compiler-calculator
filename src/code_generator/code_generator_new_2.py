class CodeGenerator:
    def __init__(self, symbol_table):
        """
        Initialize the CodeGenerator with a symbol table.
        
        :param symbol_table: A dictionary mapping variable names to their types
        """
        self.symbol_table = symbol_table
        self.register_count = 0
        self.error_encountered = False
        self.assembly_code = []

    def get_register(self):
        """
        Generate a new unique register name.
        
        :return: A new register name (e.g., 'R0', 'R1')
        """
        reg = f"R{self.register_count}"
        self.register_count += 1
        return reg

    def generate(self, parsed_output, tokenized_output):
        self.assembly_code = []
        self.error_encountered = False
        parsed_lines = list(filter(None, parsed_output.split('\n')))
        
        for i, tokens in enumerate(tokenized_output):
            self.register_count = 0
            
            if 'SyntaxError' in parsed_lines[i] or 'Undefined variable' in parsed_lines[i] or 'Index' in parsed_lines[i]:
                self.assembly_code.append('ERROR\n')
                continue
            
            token_list = tokens.split()
            parsed_line = parsed_lines[i].strip()
            
            try:
                if 'ASSIGNMENT' in tokens:
                    self._handle_assignment(token_list)
                elif 'PLUS' in tokens:
                    self._handle_addition(token_list)
                elif 'TIMES' in tokens:
                    self._handle_multiplication(token_list)
                elif 'DIVIDE' in tokens:
                    self._handle_division(token_list)
                elif 'INTEGER_DIVIDE' in tokens:
                    self._handle_integer_division(token_list)
                elif 'POW' in tokens:
                    self._handle_exponentiation(token_list)
                elif any(op in tokens for op in ['GT', 'GE', 'LT', 'LE', 'EQUAL', 'NOT_EQUAL']):
                    self._handle_comparison(token_list)
                elif 'LBRACKET' in tokens:
                    self._handle_list_operation(token_list)
                elif 'LPAREN' in tokens and 'RPAREN' in tokens:
                    self._handle_parenthesis(token_list)
                else:
                    self.assembly_code.append('# UNHANDLED OPERATION')
                    continue
            except Exception as e:
                self.assembly_code.append(f'# ERROR: {str(e)}')
                self.error_encountered = True
            
            self.assembly_code.append('')
        
        return self.assembly_code
    
    def _handle_integer_division(self, tokens):
        left_val, right_val = tokens[0].split('/')[0], tokens[2].split('/')[0]
        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()
        
        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
        self.assembly_code.append(f'DIV.i {r_result} {r_left} {r_right}')
        self.assembly_code.append(f'ST @print {r_result}')
    
    def _handle_exponentiation(self, tokens):
        left_val, right_val = tokens[0].split('/')[0], tokens[2].split('/')[0]
        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()
        
        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
        self.assembly_code.append(f'EXP.i {r_result} {r_left} {r_right}')
        self.assembly_code.append(f'ST @print {r_result}')
    
    def _handle_multiplication(self, tokens):
        values = [t.split('/')[0] for t in tokens if '/INT' in t or '/VAR' in t]
        
        if len(values) < 2:
            self.assembly_code.append("# ERROR: Multiplication requires at least two values")
            return
        
        r_prev = self.get_register()
        self.assembly_code.append(f'LD {r_prev} {self._load_value(values[0])}')
        
        for val in values[1:]:
            r_next = self.get_register()
            self.assembly_code.append(f'LD {r_next} {self._load_value(val)}')
            r_result = self.get_register()
            self.assembly_code.append(f'MUL.i {r_result} {r_prev} {r_next}')
            r_prev = r_result
        
        self.assembly_code.append(f'ST @print {r_prev}')
    
    def _handle_parenthesis(self, tokens):
        inner_tokens = [token for token in tokens if 'LPAREN' not in token and 'RPAREN' not in token]
        
        if 'PLUS' in tokens:
            self._handle_addition(inner_tokens)
        elif 'TIMES' in tokens:
            self._handle_multiplication(inner_tokens)
        elif 'DIVIDE' in tokens:
            self._handle_division(inner_tokens)
        elif 'POW' in tokens:
            self._handle_exponentiation(inner_tokens)
        elif any(op in tokens for op in ['GT', 'GE', 'LT', 'LE', 'EQUAL', 'NOT_EQUAL']):
            self._handle_comparison(inner_tokens)
        else:
            self.assembly_code.append("# ERROR: Unsupported operation inside parentheses")
    
    def _load_value(self, value):
        return f"#{value}" if value.isdigit() or value.replace('.', '', 1).isdigit() else f"@{value}"
    
    def _handle_compound_expression(self, tokens, operator):
        """
        Handles compound expressions like (h = (((1+2)+3)+4))
        Ensures step-by-step computation before final storage.
        """
        var_name = tokens[0].split('/')[0]  # The variable being assigned
        values = []  # List to store operand values
        ops = []  # List to store operators

        # Extract values and operators from the tokenized input
        for token in tokens[2:]:  # Skip the variable name and assignment operator
            if '/INT' in token or '/VAR' in token:
                values.append(token.split('/')[0])  # Extract value
            elif '/PLUS' in token:
                ops.append('PLUS')
            elif '/TIMES' in token:
                ops.append('TIMES')
            elif '/DIVIDE' in token:
                ops.append('DIVIDE')

        # Ensure we process from left to right
        r_left = self.get_register()
        self.assembly_code.append(f'LD {r_left} {self._load_value(values[0])}')

        for i in range(len(ops)):  
            r_right = self.get_register()
            self.assembly_code.append(f'LD {r_right} {self._load_value(values[i + 1])}')

            r_result = self.get_register()

            if ops[i] == 'PLUS':
                self.assembly_code.append(f'ADD.i {r_result} {r_left} {r_right}')
            elif ops[i] == 'TIMES':
                self.assembly_code.append(f'MUL.i {r_result} {r_left} {r_right}')
            elif ops[i] == 'DIVIDE':
                self.assembly_code.append(f'DIV.i {r_result} {r_left} {r_right}')
            
            r_left = r_result  # Carry result forward

        # Store final computed value in the variable
        self.assembly_code.append(f'ST @{var_name} {r_left}')
                    

    def _handle_assignment(self, tokens):
        """
        Handle variable assignment operations.
        """
        var_name = tokens[0].split('/')[0]
        value = tokens[-1].split('/')[0]
        
        r_val = self.get_register()
        self.assembly_code.append(f'LD {r_val} {self._load_value(value)}')
        self.assembly_code.append(f'ST @{var_name} {r_val}')

    def _handle_addition(self, tokens):
        """
        Handle chained addition operations properly.
        """
        values = [t.split('/')[0] for t in tokens if '/INT' in t]

        if len(values) < 2:
            self.assembly_code.append("# ERROR: Addition requires at least two values")
            return

        # Load first two values and perform the first addition
        r_prev = self.get_register()
        self.assembly_code.append(f'LD {r_prev} {self._load_value(values[0])}')
        
        for val in values[1:]:
            r_next = self.get_register()
            self.assembly_code.append(f'LD {r_next} {self._load_value(val)}')
            r_result = self.get_register()
            self.assembly_code.append(f'ADD.i {r_result} {r_prev} {r_next}')
            r_prev = r_result  # Store result in previous register for next addition

        # Final result stored in variable
        self.assembly_code.append(f'ST @{tokens[0].split("/")[0]} {r_prev}')

    def _handle_division(self, tokens):
        """
        Handle division operations.
        """
        left_val, left_type = tokens[0].split('/')[0], tokens[0].split('/')[1]
        right_val, right_type = tokens[2].split('/')[0], tokens[2].split('/')[1]

        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()

        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')

        if left_type == "REAL" or right_type == "REAL":
            if left_type == "INT":
                self.assembly_code.append(f'FL.i {r_left} {r_left}')
            if right_type == "INT":
                self.assembly_code.append(f'FL.i {r_right} {r_right}')
            self.assembly_code.append(f'DIV.f {r_result} {r_left} {r_right}')
        else:
            self.assembly_code.append(f'DIV.i {r_result} {r_left} {r_right}')

        self.assembly_code.append(f'ST @print {r_result}')

    def _handle_not_equal(self, tokens):
        """
        Handle not equal (!=) operations.
        LD R1 @x
        FL.i R0 R0
        FL.i R1 R1
        NE.f R2 R0 R1
        ST @print R2
        """
        left_val, left_type = tokens[0].split('/')[0], tokens[0].split('/')[1]
        right_val, right_type = tokens[2].split('/')[0], tokens[2].split('/')[1]

        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()

        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')

        if left_type == "INT" or left_type == "VAR":
            self.assembly_code.append(f'FL.i {r_left} {r_left}')
        if right_type == "INT" or right_type == "VAR":
            self.assembly_code.append(f'FL.i {r_right} {r_right}')
        self.assembly_code.append(f'NE.f {r_result} {r_left} {r_right}')

        self.assembly_code.append(f'ST @print {r_result}')


    def _handle_list_operation(self, tokens):
        """
        Handle all list operations including:
        1. List initialization: x = list[2]
        2. List element access: x[1]
        3. List element assignment: x[1] = 2
        4. List element arithmetic: x[0] + x[1], x[0] + 2
        """
        token_str = ' '.join(tokens)
        
        if 'ASSIGNMENT' in token_str and 'list' in token_str:
            # Case 1: List initialization
            self._handle_list_initialization(tokens)
        elif 'ASSIGNMENT' in token_str and '[' in token_str:
            # Case 3: List element assignment
            self._handle_list_element_assignment(tokens)
        elif 'PLUS' in token_str and '[' in token_str:
            # Case 4: List element arithmetic
            if token_str.count('[') == 2:
                # Case: x[0] + x[1]
                self._handle_list_element_addition(tokens)
            else:
                # Case: x[0] + 2
                self._handle_list_scalar_addition(tokens)
        else:
            # Case 2: Simple list element access
            self._handle_list_access(tokens)

    def _handle_list_initialization(self, tokens):
        """Handle list initialization (x = list[2])"""
        var_name = tokens[0].split('/')[0]
        size = tokens[4].split('/')[0]
        
        r_value = self.get_register()
        r_base = self.get_register()
        r_index = self.get_register()
        r_size = self.get_register()
        r_offset = self.get_register()
        r_addr = self.get_register()
        
        self.assembly_code.append(f'LD {r_value} #0')
        self.assembly_code.append(f'LD {r_base} @{var_name}')
        
        for i in range(int(size)):
            self.assembly_code.append(f'LD {r_index} #{i}')
            self.assembly_code.append(f'LD {r_size} #4')
            self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}')
            self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}')
            self.assembly_code.append(f'ST {r_addr} {r_value}')

    def _handle_list_access(self, tokens):
        """Handle list element access (x[1])"""
        var_name = tokens[0].split('/')[0]
        index = tokens[2].split('/')[0]
        
        r_base = self.get_register()
        r_index = self.get_register()
        r_size = self.get_register()
        r_offset = self.get_register()
        r_addr = self.get_register()
        r_value = self.get_register()
        
        self.assembly_code.append(f'LD {r_base} @{var_name}')
        self.assembly_code.append(f'LD {r_index} #{index}')
        self.assembly_code.append(f'LD {r_size} #4')
        self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}')
        self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}')
        self.assembly_code.append(f'LD {r_value} {r_addr}')
        self.assembly_code.append(f'ST @print {r_value}')

    def _handle_list_element_assignment(self, tokens):
        """Handle list element assignment (x[1] = 2)"""
        var_name = tokens[0].split('/')[0]
        index = tokens[2].split('/')[0]
        value = tokens[-1].split('/')[0]
        
        r_base = self.get_register()
        r_index = self.get_register()
        r_size = self.get_register()
        r_offset = self.get_register()
        r_addr = self.get_register()
        r_value = self.get_register()
        
        self.assembly_code.append(f'LD {r_base} @{var_name}')
        self.assembly_code.append(f'LD {r_index} #{index}')
        self.assembly_code.append(f'LD {r_size} #4')
        self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}')
        self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}')
        self.assembly_code.append(f'LD {r_value} #{value}')
        self.assembly_code.append(f'ST {r_addr} {r_value}')

    def _handle_list_element_addition(self, tokens):
        """Handle addition of two list elements (x[0] + x[1])"""
        var_name = tokens[0].split('/')[0]
        
        # Parse indices correctly from tokens
        # Find the indices by looking for the INT tokens that follow LBRACKET
        indices = []
        for i, token in enumerate(tokens):
            if '/LBRACKET' in token and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if '/INT' in next_token:
                    indices.append(next_token.split('/')[0])
        
        if len(indices) != 2:
            self.assembly_code.append('# ERROR: Invalid list indices')
            return
            
        index1, index2 = indices
        
        # First element
        r_base1 = self.get_register()
        r_index1 = self.get_register()
        r_size1 = self.get_register()
        r_offset1 = self.get_register()
        r_addr1 = self.get_register()
        r_value1 = self.get_register()
        
        # Second element
        r_base2 = self.get_register()
        r_index2 = self.get_register()
        r_size2 = self.get_register()
        r_offset2 = self.get_register()
        r_addr2 = self.get_register()
        r_value2 = self.get_register()
        
        # Result
        r_result = self.get_register()
        
        # Load first element
        self.assembly_code.append(f'LD {r_base1} @{var_name}')
        self.assembly_code.append(f'LD {r_index1} #{index1}')
        self.assembly_code.append(f'LD {r_size1} #4')
        self.assembly_code.append(f'MUL.i {r_offset1} {r_index1} {r_size1}')
        self.assembly_code.append(f'ADD.i {r_addr1} {r_base1} {r_offset1}')
        self.assembly_code.append(f'LD {r_value1} {r_addr1}')
        
        # Load second element
        self.assembly_code.append(f'LD {r_base2} @{var_name}')
        self.assembly_code.append(f'LD {r_index2} #{index2}')
        self.assembly_code.append(f'LD {r_size2} #4')
        self.assembly_code.append(f'MUL.i {r_offset2} {r_index2} {r_size2}')
        self.assembly_code.append(f'ADD.i {r_addr2} {r_base2} {r_offset2}')
        self.assembly_code.append(f'LD {r_value2} {r_addr2}')
        
        # Add elements
        self.assembly_code.append(f'ADD.i {r_result} {r_value1} {r_value2}')
        self.assembly_code.append(f'ST @print {r_result}')
        
    def _handle_list_scalar_addition(self, tokens):
        """Handle addition of list element and scalar (x[0] + 2)"""
        var_name = tokens[0].split('/')[0]
        index = tokens[2].split('/')[0]
        scalar = tokens[-1].split('/')[0]
        
        # List element
        r_base = self.get_register()
        r_index = self.get_register()
        r_size = self.get_register()
        r_offset = self.get_register()
        r_addr = self.get_register()
        r_value = self.get_register()
        
        # Scalar and result
        r_scalar = self.get_register()
        r_result = self.get_register()
        
        # Load list element
        self.assembly_code.append(f'LD {r_base} @{var_name}')
        self.assembly_code.append(f'LD {r_index} #{index}')
        self.assembly_code.append(f'LD {r_size} #4')
        self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}')
        self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}')
        self.assembly_code.append(f'LD {r_value} {r_addr}')
        
        # Load scalar and add
        self.assembly_code.append(f'LD {r_scalar} #{scalar}')
        self.assembly_code.append(f'ADD.i {r_result} {r_value} {r_scalar}')
        self.assembly_code.append(f'ST @print {r_result}')
        
# Example usage
symbol_table = {"x": "LIST", "z": "VAR", "d": "VAR", "e": "VAR", "g": "VAR"}
parsed_output = """
    (23+8)
    (2.5*0)
    SyntaxError at line 3, pos 2
    (x=5)
    (10*x)
    Undefined variable 'y' at line 6, pos 3
    (x!=5)
    (2+5)
    (x=(list[(2)]))
    (x[(1)])
    ((x[(0)])+(x[(1)]))
    Index 4 out of range for list 'x' of size 2 at line 11, pos 1
    ((x[(1)])=2)
    ((x[(0)])+2)
    (z=(3+2))
    (d=(3*2))
    (e=(3/2))
    SyntaxError at line 17, pos 7
    (g=2)
    (g=(((1+2)+3)+4))
"""

tokenized_output = [
    "23/INT +/PLUS 8/INT",
    "2.5/REAL */TIMES 0/INT",
    "5/INT NUM/VAR ^/POW 3.0/REAL",
    "x/VAR =/ASSIGNMENT 5/INT",
    "10/INT */TIMES x/VAR",
    "x/VAR =/ASSIGNMENT y/VAR",
    "x/VAR !=/NOT_EQUAL 5/INT",
    "(/LPAREN 2/INT +/PLUS 5/INT )/RPAREN",
    "x/VAR =/ASSIGNMENT list/LIST [/LBRACKET 2/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 1/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS x/VAR [/LBRACKET 1/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 4/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 1/INT ]/RBRACKET =/ASSIGNMENT 2/INT",
    "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS 2/INT",
    "z/VAR =/ASSIGNMENT 3/INT +/PLUS 2/INT",
    "d/VAR =/ASSIGNMENT 3/INT */TIMES 2/INT",
    "e/VAR =/ASSIGNMENT 3/INT //DIVIDE 2/INT",
    "f/VAR =/ASSIGNMENT 3/INT %/ERR 2/INT",
    "g/VAR =/ASSIGNMENT 2/INT",
    "g/VAR =/ASSIGNMENT 1/INT +/PLUS 2/INT +/PLUS 3/INT +/PLUS 4/INT"

]

parsed_output_test = """
    (g=(((1+2)+3)+4))
"""

tokenized_output_test = [
    "g/VAR =/ASSIGNMENT 1/INT +/PLUS 2/INT +/PLUS 3/INT +/PLUS 4/INT"
]

generator = CodeGenerator(symbol_table)
# assembly = generator.generate(parsed_output_test, tokenized_output_test)
assembly = generator.generate(parsed_output, tokenized_output)
print("\n".join(assembly))
