from dataclasses import dataclass
import csv
from typing import Any, Optional


@dataclass
class SymbolEntry:
    lexeme: str
    line_number: int
    position: int
    length: int
    token_type: str
    value: Any = None


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def insert(
        self,
        lexeme: str,
        line_number: int,
        position: int,
        token_type: str,
        value: Optional[Any] = None,
    ):
        self.symbols[lexeme] = SymbolEntry(
            lexeme=lexeme,
            line_number=line_number,
            position=position,
            length=len(lexeme),
            token_type=token_type,
            value=value,
        )

    def lookup(self, lexeme: str):
        return self.symbols.get(lexeme)

    def save_to_csv(self, filename: str):
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["lexeme", "line_number", "start_pos", "length", "type", "value"]
            )
            for entry in self.symbols.values():
                writer.writerow(
                    [
                        entry.lexeme,
                        entry.line_number,
                        entry.position,
                        entry.length,
                        entry.token_type,
                        str(entry.value) if entry.value is not None else "",
                    ]
                )

    def remove(self, lexeme):
        # Remove entry with matching lexeme if it exists
        self.symbols = {
            key: value for key, value in self.symbols.items() if key != lexeme
        }

    def get_as_dict(self):
        # symbol_table = {"x": "LIST", "z": "VAR", "d": "VAR", "e": "VAR", "g": "VAR"}
        return {key: value.token_type for key, value in self.symbols.items()}
    