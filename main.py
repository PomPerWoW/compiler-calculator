from src.lexical_analyzer.lexical_analyzer import LexicalAnalyzer
from src.symbol_table.symbol_table import SymbolTable
from src.syntax_analyzer.syntax_analyzer import SyntaxAnalyzer
from src.code_generator.code_generator_new import CodeGenerator


def compile(
<<<<<<< HEAD
    input_path,
    tok_output_path,
    grammar_output_path,
    symbol_table_path,
    lexer,
    parser,
    code_generator,
=======
    input_path, tok_output_path, grammar_output_path, symbol_table_path, lexer, parser, code_generator, assembly_output_file
>>>>>>> refs/remotes/origin/main
):
    try:
        tokenized_output = []
        with (
            open(input_path, "r") as input_file,
            open(tok_output_path, "w") as output_file,
        ):
            for line_number, line in enumerate(input_file, 1):
                if line.strip():
                    # lexical analysis
                    tokens = lexer.tokenize(line.strip(), line_number)
                    output_file.write(" ".join(tokens) + "\n")
<<<<<<< HEAD
                    tokenized_output.append(tokens)
=======
                    # tokenized_output.append(tokens)
                    tokenized_output.append(" ".join(tokens))  # Convert list to string ✅

                    
>>>>>>> refs/remotes/origin/main

                    # syntax analysis
                    try:
                        ast = parser.parse(line.strip())
<<<<<<< HEAD
                        # generator = CodeGenerator(symbol_table)
                        # # assembly = generator.generate(parsed_output_test, tokenized_output_test)
                        # assembly = code_generator.generate(ast, tokens)
=======
>>>>>>> refs/remotes/origin/main
                    except Exception as e:
                        print(f"Error in line {line_number}: {str(e)}")

        lexer.save_symbol_table(symbol_table_path)
        parser.save_parsed_output(grammar_output_path)
<<<<<<< HEAD

        # symbol_table = lexer.get_symbol_table_as_dict()
        # parse_output = parser.get_parsed_output_as_str()

        # code_generator = CodeGenerator(symbol_table)
        # code_generator.generate(parse_output, tokenized_output)
=======
        
        symbol_table = lexer.get_symbol_table_as_dict()
        parse_output = parser.get_parsed_output_as_str()
        
        code_generator = CodeGenerator(symbol_table)

        # print("parse_output: ", parse_output)
        # print("tokenized_output: ", type(tokenized_output), len(tokenized_output))
        # print(tokenized_output)
        code_generator.generate(parse_output, tokenized_output)
        
        code_generator.save_assembly(assembly_output_file)
>>>>>>> refs/remotes/origin/main

    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return False
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        return False

    return True


def main():
    input_file = "src/input/input.txt"
    tok_output_file = "src/output/laika.tok"
    symbol_table_file = "src/output/laika.csv"
    grammar_output_file = "src/output/laika.bracket"
    assembly_output_file = "src/output/laika.asm"
    symbol_table = SymbolTable()
    lexer = LexicalAnalyzer(symbol_table)
    parser = SyntaxAnalyzer(symbol_table, lexer)
    code_generator = CodeGenerator(symbol_table)

    if compile(
        input_file,
        tok_output_file,
        grammar_output_file,
        symbol_table_file,
        lexer,
        parser,
        code_generator,
<<<<<<< HEAD
=======
        assembly_output_file
>>>>>>> refs/remotes/origin/main
    ):
        print(f"Successfully processed {input_file} and generated:")
        print(f"- Symbol Table: {symbol_table_file}")
        print(f"- Tokens: {tok_output_file}")
        print(f"- Parsed Output: {grammar_output_file}")
        print(f"- Assembly Code: {assembly_output_file}")
    else:
        print("Failed to process files")


if __name__ == "__main__":
    main()
