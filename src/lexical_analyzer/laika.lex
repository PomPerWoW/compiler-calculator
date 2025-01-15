# Lexical Grammar for Calculator Language

# Variables
VAR             [a-zA-Z_][a-zA-Z0-9_]*

# Keywords
LIST            list

# Numbers
INT             (0|[1-9][0-9]*)
REAL            (0|[1-9][0-9]*)?\.([0-9]+)?([Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+

# Operators
PLUS                    \+
MINUS                   \-
TIMES                   \*
DIVIDE                  /
INTEGER_DIVISION        //
POW                     \^
GREATER_THAN            \>
GREATER_THAN_OR_EQUAL   \>=
LESS_THAN               \<
LESS_THAN_OR_EQUAL      \<=
EQUAL_TO                \==
NOT_EQUAL               \!=
ASSIGNMENT              \=

# Parentheses and Brackets
LPAREN          \(
RPAREN          \)
LBRACKET        \[
RBRACKET        \]

# Error tokens (any other special symbols)
ERR             [^a-zA-Z0-9\+\-\*\/\^\=\!\(\)\[\]\s\.]+ 
