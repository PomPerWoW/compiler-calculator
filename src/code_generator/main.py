class CodeGenerator:
    def __init__(self, symbol_table):
        self.synbol_table = symbol_table
        self.register_count = 0
        self.assembly_code = []
        
    def get_register(self):
        reg = f"R{self.register_count}"
        self.register_count += 1
        return reg
    
    def generate_code(self, parsed_output, tokenized_output):
        self.assembly_code = []
        parsed_line = parsed_output.split("\n")
        for i, line in enumerate(parsed_line):
            if "SyntaxError" in line:
                self.assembly_code.append(f"ERROR")
                continue
            tokens = tokenized_output[i].split()
            if "Undefined variable" in line:
                self.assembly_code.append(f"ERROR")
                continue
            # self.generate_instruction(tokens)
            # pass


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

tokenized_output = [
    "23/INT +/PLUS 8/INT",
    "2.5/REAL */TIMES 0/INT",
    "5/INT NUM/VAR ^/POW 3.0/REAL",
    "x/VAR =/ASSIGNMENT 5/INT",
    "10/INT */TIMES x/VAR",
    "x/VAR =/ASSIGNMENT y/VAR",
    "x/VAR !=/NOT_EQUAL 5/INT",
    "(/LPAREN 2/INT +/PLUS 5/INT )/RPAREN",
]


generator = CodeGenerator(symbol_table)
assembly = generator.generate_code(parsed_output, tokenized_output)
print("\n".join(assembly))