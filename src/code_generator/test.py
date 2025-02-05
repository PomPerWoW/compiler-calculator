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
        """
        Generate assembly-like instructions from parsed and tokenized outputs.
        """
        self.assembly_code = []
        self.error_encountered = False
        parsed_lines = parsed_output.split('\n')
        parsed_lines = list(filter(None, parsed_lines))
                
        for i, tokens in enumerate(tokenized_output):
            if 'SyntaxError' in parsed_lines[i] or 'Undefined variable' in parsed_lines[i] or 'Index out of range' in parsed_lines[i]:
                self.assembly_code.append('ERROR\n')
                continue
            
            token_list = tokens.split()
            parsed_line = parsed_lines[i].strip()
            
            try:
                # First check for explicit parentheses tokens
                if 'LPAREN' in tokens and 'RPAREN' in tokens:
                    # Filter out parentheses tokens and handle inner expression
                    inner_tokens = [token for token in token_list if 'LPAREN' not in token and 'RPAREN' not in token]
                    if 'PLUS' in tokens:
                        self._handle_addition(inner_tokens)
                    elif 'TIMES' in tokens:
                        self._handle_multiplication(inner_tokens)
                    elif 'DIVIDE' in tokens:
                        self._handle_division(inner_tokens)
                # Then check for compound expressions
                elif parsed_line.startswith('(') and '=' in parsed_line and ('+' in parsed_line or '*' in parsed_line or '/' in parsed_line):
                    operator = None
                    if '+' in parsed_line:
                        operator = 'PLUS'
                    elif '*' in parsed_line:
                        operator = 'TIMES'
                    elif '/' in parsed_line:
                        operator = 'DIVIDE'
                    self._handle_compound_expression(token_list, operator)
                elif 'LBRACKET' in tokens:
                    self._handle_list_operation(token_list)
                elif 'ASSIGNMENT' in tokens:
                    self._handle_assignment(token_list)
                elif 'PLUS' in tokens:
                    self._handle_addition(token_list)
                elif 'TIMES' in tokens:
                    self._handle_multiplication(token_list)
                elif 'DIVIDE' in tokens:
                    self._handle_division(token_list)
                elif 'NOT_EQUAL' in tokens:
                    self._handle_not_equal(token_list)
                else:
                    self.assembly_code.append('# UNHANDLED OPERATION')
                    continue
            except Exception as e:
                self.assembly_code.append(f'# ERROR: {str(e)}')
                self.error_encountered = True
                
            self.assembly_code.append('')
        
        return self.assembly_code
    def _handle_compound_expression(self, tokens, operator):
        """
        Handle compound expressions like (z=(3+2)), (d=(3*2)), (e=(3/2))
        """
        # Parse out the components
        var_name = tokens[0].split('/')[0]
        left_val = tokens[2].split('/')[0]
        right_val = tokens[4].split('/')[0]
        
        # Get registers
        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()
        
        # Generate assembly code
        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
        
        if operator == 'PLUS':
            self.assembly_code.append(f'ADD.i {r_result} {r_left} {r_right}')
        elif operator == 'TIMES':
            self.assembly_code.append(f'MUL.i {r_result} {r_left} {r_right}')
        elif operator == 'DIVIDE':
            self.assembly_code.append(f'DIV.i {r_result} {r_left} {r_right}')
        elif operator == 'NOT_EQUAL':
            self.assembly_code.append(f'NE.f {r_result} {r_left} {r_right}')
        elif operator == 'ASSIGNMENT':
            self.assembly_code.append(f'ST @{var_name} {r_result}')            
            
        self.assembly_code.append(f'ST @{var_name} {r_result}')
        
    def _load_value(self, value):
        """Returns correctly formatted value loading instruction"""
        return f"#{value}" if value.isdigit() or value.replace('.', '', 1).isdigit() else f"@{value}"

    def _handle_parenthesis(self, tokens):
        """
        Handle expressions within parentheses by processing the inner expression.
        Now handles nested expressions properly.
        """
        # Filter out the outer LPAREN/RPAREN tokens
        inner_tokens = [token for token in tokens if 'LPAREN' not in token and 'RPAREN' not in token]
        
        # Check for assignment with expression
        if any('ASSIGNMENT' in token for token in inner_tokens):
            # Find position of ASSIGNMENT
            assign_pos = next(i for i, token in enumerate(inner_tokens) if 'ASSIGNMENT' in token)
            var_name = inner_tokens[0].split('/')[0]
            
            # Process right-hand side expression
            right_tokens = inner_tokens[assign_pos + 1:]
            
            if any('PLUS' in token for token in right_tokens):
                # Handle addition first
                left_val = right_tokens[0].split('/')[0]
                right_val = right_tokens[2].split('/')[0]
                
                r_left = self.get_register()
                r_right = self.get_register()
                r_result = self.get_register()
                
                self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
                self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
                self.assembly_code.append(f'ADD.i {r_result} {r_left} {r_right}')
                self.assembly_code.append(f'ST @{var_name} {r_result}')
            
            elif any('TIMES' in token for token in right_tokens):
                # Handle multiplication first
                left_val = right_tokens[0].split('/')[0]
                right_val = right_tokens[2].split('/')[0]
                
                r_left = self.get_register()
                r_right = self.get_register()
                r_result = self.get_register()
                
                self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
                self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
                self.assembly_code.append(f'MUL.i {r_result} {r_left} {r_right}')
                self.assembly_code.append(f'ST @{var_name} {r_result}')
                
            elif any('DIVIDE' in token for token in right_tokens):
                # Handle division first
                left_val = right_tokens[0].split('/')[0]
                right_val = right_tokens[2].split('/')[0]
                
                r_left = self.get_register()
                r_right = self.get_register()
                r_result = self.get_register()
                
                self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
                self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
                self.assembly_code.append(f'DIV.i {r_result} {r_left} {r_right}')
                self.assembly_code.append(f'ST @{var_name} {r_result}')
            
            else:
                # Simple assignment
                value = right_tokens[0].split('/')[0]
                r_val = self.get_register()
                self.assembly_code.append(f'LD {r_val} {self._load_value(value)}')
                self.assembly_code.append(f'ST @{var_name} {r_val}')
        
        else:
            # Handle non-assignment expressions
            if any('PLUS' in token for token in inner_tokens):
                self._handle_addition(inner_tokens)
            elif any('TIMES' in token for token in inner_tokens):
                self._handle_multiplication(inner_tokens)
            elif any('DIVIDE' in token for token in inner_tokens):
                self._handle_division(inner_tokens)
            elif any('NOT_EQUAL' in token for token in inner_tokens):
                self._handle_not_equal(inner_tokens)
                

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
        Handle addition operations.
        """
        left_val = tokens[0].split('/')[0]
        right_val = tokens[2].split('/')[0]

        r_left = self.get_register()
        r_right = self.get_register()
        r_result = self.get_register()

        self.assembly_code.append(f'LD {r_left} {self._load_value(left_val)}')
        self.assembly_code.append(f'LD {r_right} {self._load_value(right_val)}')
        self.assembly_code.append(f'ADD.i {r_result} {r_left} {r_right}')
        self.assembly_code.append(f'ST @print {r_result}')

    def _handle_multiplication(self, tokens):
        """
        Handle multiplication operations.
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
            self.assembly_code.append(f'MUL.f {r_result} {r_left} {r_right}')
        else:
            self.assembly_code.append(f'MUL.i {r_result} {r_left} {r_right}')

        self.assembly_code.append(f'ST @print {r_result}')

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
        Handle list initialization and list element operations.
        Supports list creation, element assignment, and element access.
        """
        # Parse the tokens carefully
        var_name = tokens[0].split('/')[0]
        
        # Check different list operation scenarios
        if len(tokens) > 2 and 'LBRACKET' in tokens[1] and 'RBRACKET' in tokens[3]:
            # List initialization: x = list[size]
            if 'list' in " ".join(tokens):
                size = tokens[4].split('/')[0]
                
                # Get registers for the operation
                r_value = self.get_register()
                r_base = self.get_register()
                r_size = self.get_register()
                r_index = self.get_register()
                r_offset = self.get_register()
                r_addr = self.get_register()
                
                # Load 0 as initial value
                self.assembly_code.append(f'LD {r_value} #0    // Initialize list {var_name} with zeros')
                
                # Create list by storing base address
                self.assembly_code.append(f'ST @{var_name}_size #{size}    // Store list size')
                
                # Allocate space for list and initialize elements to 0
                for i in range(int(size)):
                    # Load current index
                    self.assembly_code.append(f'LD {r_index} #{i}    // List index {i}')
                    
                    # Load element size (4 bytes)
                    self.assembly_code.append(f'LD {r_size} #4    // Element size = 4 bytes')
                    
                    # Calculate offset
                    self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}    // Calculate memory offset')
                    
                    # Calculate absolute address for this list element
                    self.assembly_code.append(f'LD {r_base} @{var_name}    // Load list base address')
                    self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}    // Calculate element address')
                    
                    # Store 0 at calculated address
                    self.assembly_code.append(f'ST {r_addr} {r_value}    // Initialize {var_name}[{i}] = 0')
            
            # List element access: x[index] or x[index] = value
            else:
                index = tokens[2].split('/')[0]
                r_base = self.get_register()
                r_index = self.get_register()
                r_size = self.get_register()
                r_offset = self.get_register()
                r_addr = self.get_register()
                
                # Load base address of list
                self.assembly_code.append(f'LD {r_base} @{var_name}    // Load list base address')
                
                # Load index
                self.assembly_code.append(f'LD {r_index} #{index}    // Load list index')
                
                # Load element size
                self.assembly_code.append(f'LD {r_size} #4    // Element size = 4 bytes')
                
                # Calculate memory offset
                self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}    // Calculate memory offset')
                
                # Calculate absolute address
                self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}    // Calculate element address')
                
                # If it's an assignment: x[index] = value
                if len(tokens) > 4 and tokens[3] == '=/ASSIGNMENT':
                    value = tokens[4].split('/')[0]
                    r_value = self.get_register()
                    self.assembly_code.append(f'LD {r_value} {self._load_value(value)}    // Load value')
                    self.assembly_code.append(f'ST {r_addr} {r_value}    // Store value in list element')
                else:
                    # If it's just accessing: x[index]
                    r_value = self.get_register()
                    self.assembly_code.append(f'LD {r_value} {r_addr}    // Load list element value')
                    self.assembly_code.append(f'ST @print {r_value}    // Print list element')

    
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
    ((x[(0)])+(x[(1)]))
    Index 4 out of range for list 'x' of size 2 at line 11, pos 1
    ((x[(1)])=2)
    ((x[(0)])+2)
    (z=(3+2))
    (d=(3*2))
    (e=(3/2))
    SyntaxError at line 17, pos 7
    (g=2)
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
    "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS x/VAR [/LBRACKET 1/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 4/INT ]/RBRACKET",
    "x/VAR [/LBRACKET 1/INT ]/RBRACKET =/ASSIGNMENT 2/INT",
    "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS 2/INT",
    "z/VAR =/ASSIGNMENT 3/INT +/PLUS 2/INT",
    "d/VAR =/ASSIGNMENT 3/INT */TIMES 2/INT",
    "e/VAR =/ASSIGNMENT 3/INT //DIVIDE 2/INT",
    "f/VAR =/ASSIGNMENT 3/INT %/ERR 2/INT",
    "g/VAR =/ASSIGNMENT 2/INT",
]

parsed_output_test = """
    (2+5)
"""

tokenized_output_test = [
    "(/LPAREN 2/INT +/PLUS 5/INT )/RPAREN",
]

generator = CodeGenerator(symbol_table)
# assembly = generator.generate(parsed_output_test, tokenized_output_test)
assembly = generator.generate(parsed_output, tokenized_output)
print("\n".join(assembly))

# LD R0 #23
# LD R1 #8
# ADD.i R2 R0 R1
# ST @print R2

# LD R0 #2.5
# LD R1 #0
# FL.i R1 R1
# MUL.f R2 R0 R1
# ST @print R2

# ERROR

# LD R0 #5
# ST @x R0
# LD R0 #10
# LD R1 @x
# MUL.i R2 R0 R1
# ST @print R2

# ERROR

# LD R0 5
# LD R1 @x
# FL.i R0 R0
# FL.i R1 R1
# NE.f R2 R0 R1
# ST @print R2

# LD R0 #0 LD R1 @x // load 0, list x[2] we should set x[0] and x[1] to 0
# // load base address of x
# LD R2 #0 // load offset 0
# LD R3 #4 // size = 4 bytes
# MUL.i R4 R2 R3 // offset * size
# ADD.i R5 R1 R4 // x[0] address
# ST R5 R0 // x[0] = 0
# LD R2 #1
# LD R3 #4
# MUL.i R4 R2 R3
# ADD.i R5 R1 R4 // x[1] address
# ST R5 R0 // x[1] = 0
# LD R0 @x
# LD R1 #1
# LD R2 #4
# MUL.i R3 R1 R2
# ADD.i R4 R0 R3
# ST $print R4 // print x[1]
