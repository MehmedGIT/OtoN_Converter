from .utils import (
    extract_line_tokens,
    extract_ocrd_command,
    validate_first_line,
    validate_middle_line,
    validate_last_line,
    validate_line_token_symbols,
)


# TODO: More refactoring needed - still not satisfied with the readability.
# Some methods could be simplified with better algorithms
class OCRD_Validator:
    def __init__(self):
        pass

    def extract_ocrd_tokens(self, ocrd_lines):
        ocrd_tokens = []
        for line in ocrd_lines:
            curr_line_tokens = extract_line_tokens(line)
            if len(curr_line_tokens) > 0:
                ocrd_tokens.append(curr_line_tokens)

        return ocrd_tokens

    def validate_ocrd_token_symbols(self, ocrd_lines):
        # Rule 1: A single char token must be either: QM or BACKSLASH
        # Rule 2: A double char token must be either: -I, -O, or -P
        # Rule 3: Other tokens must contain only VALID_CHARS

        # Check for invalid symbols/tokens
        for line_index in range(0, len(ocrd_lines)):
            validate_line_token_symbols(line_index, ocrd_lines[line_index])

    def validate_ocrd_lines(self, ocrd_lines):
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
        validate_first_line(ocrd_lines[0])

        last_line_number = len(ocrd_lines) - 1
        for line_index in range(1, last_line_number):
            validate_middle_line(line_index, ocrd_lines[line_index])

        validate_last_line(last_line_number, ocrd_lines[-1])

    def extract_ocrd_commands(self, ocrd_lines):
        ocrd_commands = []
        for line_index in range(1, len(ocrd_lines)):
            ocrd_command = extract_ocrd_command(ocrd_lines[line_index])
            ocrd_commands.append(ocrd_command)
        return ocrd_commands
