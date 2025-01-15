from src.lexical_analyzer.lexical_analyzer import LexicalAnalyzer
from src.syntax_analyzer.syntax_analyzer import SyntaxAnalyzer


def tokenize_expression(expression, output_file, lexer):
    # print(f"\nTokenizing expression: {expression}")
    # print("-" * 40)
    tokens = lexer.tokenize(expression)
    output_file.write(" ".join(tokens) + "\n")


def process_input_file(
    input_path, tok_output_path, grammar_output_path, symbol_table_path, lexer
):
    try:
        syntax_analyzer = SyntaxAnalyzer()

        with open(input_path, "r") as input_file, open(
            tok_output_path, "w"
        ) as output_file:
            for line_number, line in enumerate(input_file, 1):
                if line.strip():
                    # First do lexical analysis
                    tokens = lexer.tokenize(line.strip())
                    output_file.write(" ".join(tokens) + "\n")

                    # Then do syntax analysis
                    try:
                        ast = syntax_analyzer.parse(line.strip(), line_number)
                        if ast:
                            print(f"AST: {ast}")
                    except Exception as e:
                        print(f"Error in line {line_number}: {str(e)}")

        lexer.save_symbol_table(symbol_table_path)
        syntax_analyzer.save_parsed_output(grammar_output_path)

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
    lexer = LexicalAnalyzer()

    if process_input_file(
        input_file, tok_output_file, grammar_output_file, symbol_table_file, lexer
    ):
        print(f"Successfully processed {input_file} and generated:")
        print(f"- Symbol Table: {symbol_table_file}")
        print(f"- Tokens: {tok_output_file}")
        print(f"- Parsed Output: {grammar_output_file}")
    else:
        print("Failed to process files")


if __name__ == "__main__":
    main()
