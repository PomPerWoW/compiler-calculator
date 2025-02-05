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
        
        :param parsed_output: String containing parsed expressions and errors
        :param tokenized_output: List of tokenized expressions
        :return: List of assembly-like instructions
        """
        self.assembly_code = []
        self.error_encountered = False
        parsed_lines = parsed_output.split('\n')
        # remove '' from parsed_lines list
        parsed_lines = list(filter(None, parsed_lines))
                
        for i, tokens in enumerate(tokenized_output):
            # if self.error_encountered:
            #     continue
            
            if 'SyntaxError' in parsed_lines[i] or 'Undefined variable' in parsed_lines[i] or 'Index out of range' in parsed_lines[i]:
                self.assembly_code.append('ERROR\n')
                continue
            
            token_list = tokens.split()
            
            try:
                # Handle different operations
                # handle (
                if 'LPAREN' in tokens:
                    self._handle_parenthesis(token_list)
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

    def _load_value(self, value):
        """Returns correctly formatted value loading instruction"""
        return f"#{value}" if value.isdigit() or value.replace('.', '', 1).isdigit() else f"@{value}"

    def _handle_parenthesis(self, tokens):
        """
        Handle expressions within parentheses by processing the inner expression.
        Ignores the parentheses tokens and processes the content within.
        """
        # Filter out parenthesis tokens
        inner_tokens = [token for token in tokens if 'LPAREN' not in token and 'RPAREN' not in token]
        
        # Check what operation is inside the parentheses
        if any('LBRACKET' in token for token in inner_tokens):
            self._handle_list_operation(inner_tokens)
        elif any('PLUS' in token for token in inner_tokens):
            self._handle_addition(inner_tokens)
        elif any('TIMES' in token for token in inner_tokens):
            self._handle_multiplication(inner_tokens)
        elif any('DIVIDE' in token for token in inner_tokens):
            self._handle_division(inner_tokens)
        elif any('NOT_EQUAL' in token for token in inner_tokens):
            self._handle_not_equal(inner_tokens)
        elif any('ASSIGNMENT' in token for token in inner_tokens):
            self._handle_assignment(inner_tokens)
        else:
            self.assembly_code.append('# UNHANDLED OPERATION INSIDE PARENTHESES')
            

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
        Handle list initialization with a given size.
        Example: x = list[2] should initialize a list of size 2 with zeros
        """
        # Get variable name and size
        var_name = tokens[0].split('/')[0]  # x
        size = tokens[4].split('/')[0]      # 2
        
        # Get registers for the operation
        r_value = self.get_register()  # R0 in original
        r_base = self.get_register()   # R1 in original
        r_index = self.get_register()  # R2 in original
        r_size = self.get_register()   # R3 in original
        r_offset = self.get_register() # R4 in original
        r_addr = self.get_register()   # R5 in original
        
        # Load 0 into first register (value to initialize list elements with)
        self.assembly_code.append(f'LD {r_value} #0    // load 0, list {var_name}[{size}] we should set {var_name}[0] and {var_name}[1] to 0')
        
        # Load base address of list
        self.assembly_code.append(f'LD {r_base} @{var_name}    // load base address of {var_name}')
        
        # Initialize each element to 0
        for i in range(int(size)):
            # Load current index
            self.assembly_code.append(f'LD {r_index} #{i}    // load offset {i}')
            
            # Load element size (4 bytes)
            self.assembly_code.append(f'LD {r_size} #4    // size = 4 bytes')
            
            # Calculate offset
            self.assembly_code.append(f'MUL.i {r_offset} {r_index} {r_size}    // offset * size')
            
            # Calculate address
            self.assembly_code.append(f'ADD.i {r_addr} {r_base} {r_offset}    // {var_name}[{i}] address')
            
            # Store 0 at calculated address
            self.assembly_code.append(f'ST {r_addr} {r_value}    // {var_name}[{i}] = 0')

    
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
"""
# (x=(list[(2)]))
# (([x0])+([x1]))
# Index 4 out of range for list 'x' of size 2 at line 11, pos 1
# (x[(1)]=(2))
# (([x0])+2)
# (z=(3+2))
# (d=(3*2))
# (e=(3/2))
# SyntaxError at line 17, pos 7
# (g=2)"""

tokenized_output = [
    "23/INT +/PLUS 8/INT",
    "2.5/REAL */TIMES 0/INT",
    "5/INT NUM/VAR ^/POW 3.0/REAL",
    "x/VAR =/ASSIGNMENT 5/INT",
    "10/INT */TIMES x/VAR",
    "x/VAR =/ASSIGNMENT y/VAR",
    "x/VAR !=/NOT_EQUAL 5/INT",
    "(/LPAREN 2/INT +/PLUS 5/INT )/RPAREN",
    # "x/VAR =/ASSIGNMENT list/LIST [/LBRACKET 2/INT ]/RBRACKET",
    # "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS x/VAR [/LBRACKET 1/INT ]/RBRACKET",
    # "x/VAR [/LBRACKET 4/INT ]/RBRACKET",
    # "x/VAR [/LBRACKET 1/INT ]/RBRACKET =/ASSIGNMENT 2/INT",
    # "x/VAR [/LBRACKET 0/INT ]/RBRACKET +/PLUS 2/INT",
    # "z/VAR =/ASSIGNMENT 3/INT +/PLUS 2/INT",
    # "d/VAR =/ASSIGNMENT 3/INT */TIMES 2/INT",
    # "e/VAR =/ASSIGNMENT 3/INT //DIVIDE 2/INT",
    # "f/VAR =/ASSIGNMENT 3/INT %/ERR 2/INT",
    # "g/VAR =/ASSIGNMENT 2/INT"
]

parsed_output_test = """
# (z=(3+2))
# (d=(3*2))
# (e=(3/2))
# SyntaxError at line 17, pos 7
# (g=2)
"""

tokenized_output_test = [
    "z/VAR =/ASSIGNMENT 3/INT +/PLUS 2/INT",
    "d/VAR =/ASSIGNMENT 3/INT */TIMES 2/INT",
    "e/VAR =/ASSIGNMENT 3/INT //DIVIDE 2/INT",
    "f/VAR =/ASSIGNMENT 3/INT %/ERR 2/INT",
    "g/VAR =/ASSIGNMENT 2/INT"
]

generator = CodeGenerator(symbol_table)
assembly = generator.generate(parsed_output_test, tokenized_output_test)
# assembly = generator.generate(parsed_output, tokenized_output)
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
