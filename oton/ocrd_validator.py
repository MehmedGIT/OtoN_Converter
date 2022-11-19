from .utils import (
    is_valid_file_path,
    extract_file_lines,
    extract_line_tokens,
    extract_ocrd_command,
    validate_first_line,
    validate_middle_line,
    validate_last_line,
    print_syntax_error,
    validate_single_len_token_symbols,
    validate_double_len_token_symbols,
    validate_token_symbols,
)

# TODO: More refactoring needed - still not satisfied with the readability.
# Some methods could be simplified with better algorithms
class OCRD_Validator:
    def __init__(self):
        pass

    def extract_ocrd_commands(self, ocrd_lines):
        ocrd_commands = []

        for line_index in range(1, len(ocrd_lines)):
            ocrd_command = extract_ocrd_command(ocrd_lines[line_index])
            ocrd_commands.append(ocrd_command)

        return ocrd_commands

    def extract_and_validate_ocrd_file(self, filepath):
        is_valid_file_path(filepath)
        file_lines = extract_file_lines(filepath)
        ocrd_tokens = self._extract_ocrd_tokens(file_lines)
        self._validate_ocrd_lines(ocrd_tokens)
        self._validate_ocrd_token_symbols(ocrd_tokens)
        # TODO: Deactivated - must be refactored
        # self._validate_ocrd_io_order(ocrd_lines)

        return ocrd_tokens

    def _extract_ocrd_tokens(self, ocrd_lines):
        ocrd_tokens = []
        for line in ocrd_lines:
            curr_line_tokens = extract_line_tokens(line)
            if len(curr_line_tokens) > 0:
                ocrd_tokens.append(curr_line_tokens)

        return ocrd_tokens

    def _validate_ocrd_lines(self, ocrd_lines):
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

        for line_index in range(1, len(ocrd_lines)-1):
            validate_middle_line(line_index, ocrd_lines[line_index])

        validate_last_line(len(ocrd_lines)-1, ocrd_lines[-1])

    def _validate_ocrd_token_symbols(self, ocrd_lines):
        # Rule 1: A single char token must be either: QM or BACKSLASH
        # Rule 2: A double char token must be either: -I, -O, or -P
        # Rule 3: Other tokens must contain only VALID_CHARS

        # Check for invalid symbols/tokens
        for line_index in range (0, len(ocrd_lines)):
            for token_index in range(0, len(ocrd_lines[line_index])):
                current_token = ocrd_lines[line_index][token_index]
                if len(current_token) == 1:
                    validate_single_len_token_symbols(line_index, token_index, current_token)
                elif len(current_token) == 2:
                    validate_double_len_token_symbols(line_index, token_index, current_token)
                else:
                    validate_token_symbols(line_index, current_token)

    # TODO: This is temporarily deactivated and the user must be responsible for the correct 
    # input/output folder sequences. There are cases in which the -I parameter may take 2/3 folders.
    # This should be implemented properly when refactoring the code
    """
    def _validate_ocrd_io_order(self, ocrd_lines):
        # Rule 1: The input parameter of the second line is the entry-point
        # Rule 2: The input parameter of lines after the second line 
        # are the output parameters of the previous line 
        prev_output = None
        curr_input = None
        curr_output = None

        for line_index in range (1, len(ocrd_lines)):
            curr_line = ocrd_lines[line_index]
            curr_input = curr_line[curr_line.index('-I')+1]
            curr_output = curr_line[curr_line.index('-O')+1]

            if prev_output is not None:
                if prev_output != curr_input:
                    info = "Input/Output mismatch error!"
                    hint = f"{prev_output} on line {line_index} does not match with {curr_input} on line {line_index+1}"
                    self.__print_syntax_error(line_num=line_index+1, info=info, hint=hint)

            prev_output = 
    """


