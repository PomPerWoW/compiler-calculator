from src.lexical_analyzer.lexical_analyzer import LexicalAnalyzer


def tokenize_expression(expression, output_file, lexer):
    print(f"\nTokenizing expression: {expression}")
    print("-" * 40)
    tokens = lexer.tokenize(expression)
    output_file.write(" ".join(tokens) + "\n")


def process_input_file(input_path, output_path, symbol_table_path, lexer):
    try:
        with open(input_path, "r") as input_file, open(output_path, "w") as output_file:
            for line in input_file:
                if line.strip():
                    tokenize_expression(line.strip(), output_file, lexer)

        lexer.save_symbol_table(symbol_table_path)

    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return False
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        return False

    return True


def main():
    input_file = "src/input/input.txt"
    output_file = "src/output/laika.tok"
    symbol_table_file = "src/output/laika.csv"
    lexer = LexicalAnalyzer()

    if process_input_file(input_file, output_file, symbol_table_file, lexer):
        print(f"Successfully processed {input_file} and generated:")
        print(f"- Tokens: {output_file}")
        print(f"- Symbol Table: {symbol_table_file}")
    else:
        print("Failed to process files")


if __name__ == "__main__":
    main()
