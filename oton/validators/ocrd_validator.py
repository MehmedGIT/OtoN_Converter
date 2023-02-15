from .validator_utils import (
    validate_first_line,
    validate_middle_line,
    validate_last_line,
    validate_line_token_symbols,
)


# TODO: More refactoring needed - still not satisfied with the readability.
# Some methods could be simplified with better algorithms
class OCRDValidator:
    def __init__(self):
        pass

    def validate_ocrd_lines(self, ocrd_lines):
        # Token Rules:
        # Rule 1: A single char token must be either: QM or BACKSLASH
        # Rule 2: A double char token must be either: -I, -O, or -P
        # Rule 3: Other tokens must contain only VALID_CHARS

        # Line Rules:
        # Rule 1: The first line starts with 'ocrd process \'
        # Rule 2: Validate the minimum amount of tokens needed
        # Rule 3: Validate the start of an OCR-D command
        # Rule 4: Validate the OCR-D processor call in the OCR-D command
        # Rule 5: After a '-I' token on each line only one argument must follow
        # Rule 6: After a '-O' token on each line only one argument must follow
        # Rule 7: After a '-P' token on each line only two arguments must follow
        # Rule 8: Only one '-I' and one '-O' token are allowed on each line
        # Rule 9: Multiple '-P' tokens are allowed on each line
        # Rule 10. The order of '-I', '-O', and '-P' does not matter
        # Warning: -P are not checked if they are supported or not by the specific OCR-D processors
        # Rule 11: Validate the end of an OCR-D command
        # Rule 12: Each line except the last one ends with a backslash (BACKSLASH)
        validate_line_token_symbols(0, ocrd_lines[0])
        validate_first_line(ocrd_lines[0])

        last_line_number = len(ocrd_lines) - 1
        for line_index in range(1, last_line_number):
            validate_line_token_symbols(line_index, ocrd_lines[line_index])
            validate_middle_line(line_index, ocrd_lines[line_index])

        validate_line_token_symbols(last_line_number, ocrd_lines[-1])
        validate_last_line(last_line_number, ocrd_lines[-1])
