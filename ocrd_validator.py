import sys
from os.path import exists, isfile
from string import ascii_letters, digits

from ocrd_processors_list import OCRD_PROCESSORS

# Valid characters to be used in the ocrd file
VALID_CHARS = f'-_.{ascii_letters}{digits}'

# SYMBOLS
BACKSLASH = '\\'
# Quotation Mark
QM = '"'
SPACE = ' '

class OCRD_Validator:
    def __init__(self):
        # ocrd_lines holds the number of lines of the input Ocrd file
        # for each line an inner list is created to hold separate tokens of that line
        self.ocrd_lines = []

    def extract_ocrd_commands(self):
        ocrd_commands = []
        for line_index in range(1, len(self.ocrd_lines)):
            first_qm_index = 0
            last_qm_index = 0

            for token_index in range(1, len(self.ocrd_lines[line_index])):
                curr_token = self.ocrd_lines[line_index][token_index]
                if curr_token == QM:
                    last_qm_index = token_index
                    break

            line = self.ocrd_lines[line_index]
            # Append ocrd- as a prefix
            line[first_qm_index+1] = f"ocrd-{line[first_qm_index+1]}"
            # Extract the ocr-d command without quotation marks
            sub_line = line[first_qm_index+1:last_qm_index]
            ocrd_commands.append(sub_line)

        return ocrd_commands

    def validate_ocrd_file(self, filepath):
        self._validate_ocrd_file_path(filepath)
        self._extract_ocrd_tokens(filepath)
        self._validate_ocrd_lines()
        self._validate_ocrd_token_symbols()
        self._validate_ocrd_io_order()

    def _validate_ocrd_file_path(self, filepath):
        if not exists(filepath):
            print(f"OCR-D file: {filepath} does not exist!")
            sys.exit(2)
        if not isfile(filepath):
            print(f"OCR-D file: {filepath} is not a readable file!")
            sys.exit(2)

    # Rule 1: Each QM and BACKSLASH is a separate token
    # Rule 2: Each ocrd-process is a separate token
    # Rule 3: Each -I, -O, and -P is a separate token
    def _extract_ocrd_tokens(self, filepath):
        self.ocrd_lines = []

        # Extract tokens from the ocrd_file
        # Unnecessary empty spaces/lines are discarded
        with open(filepath, mode='r', encoding='utf-8') as ocrd_file:
            for line in ocrd_file:
                curr_line_tokens = []
                line = line.strip().split(SPACE)
                for token in line:
                    if len(token) == 0:
                        continue
                    # Create separate tokens
                    # for quotation marks
                    if token.startswith(QM):
                        curr_line_tokens.append(QM)
                        curr_line_tokens.append(token[1:])
                    elif token.endswith(QM):
                        curr_line_tokens.append(token[:-1])
                        curr_line_tokens.append(QM)
                    else:
                        curr_line_tokens.append(token)

                if len(curr_line_tokens) > 0:
                    self.ocrd_lines.append(curr_line_tokens)

    # Rule 1: The input parameter of the second line is the entry-point
    # Rule 2: The input parameter of lines after the second line 
    # are the output parameters of the previous line 
    def _validate_ocrd_io_order(self):
        prev_output = None
        curr_input = None
        curr_output = None

        for line_index in range (1, len(self.ocrd_lines)):
            curr_line = self.ocrd_lines[line_index]
            curr_input = curr_line[curr_line.index('-I')+1]
            curr_output = curr_line[curr_line.index('-O')+1]

            if prev_output is not None:
                if prev_output != curr_input:
                    info = "Input/Output mismatch error!"
                    hint = f"{prev_output} on line {line_index} does not match with {curr_input} on line {line_index+1}"
                    self.__print_syntax_error(line_num=line_index+1, info=info, hint=hint)

            prev_output = curr_output

    # Rule 1: A single char token must be either: QM or BACKSLASH
    # Rule 2: A double char token must be either: -I, -O, or -P
    # Rule 3: Other tokens must contain only VALID_CHARS
    def _validate_ocrd_token_symbols(self):
        # Check for invalid symbols/tokens
        for line_index in range (0, len(self.ocrd_lines)):
            for token_index in range(0, len(self.ocrd_lines[line_index])):
                current_token = self.ocrd_lines[line_index][token_index]
                if len(current_token) == 1:
                    self.__validate_single_len_token_symbols(line_index, token_index, current_token)
                elif len(current_token) == 2:
                    self.__validate_double_len_token_symbols(line_index, token_index, current_token)
                else:
                    self.__validate_token_symbols(line_index, current_token)

    def __validate_single_len_token_symbols(self, line_index, token_index, token):
        if token in (QM, BACKSLASH):
            return True
        else:
            info = f"TOKEN_ERROR_RULE_01: Invalid token: {token}"
            hint = "Single len tokens can be either a quotation mark or a backslash."
            self.__print_syntax_error(line_num=line_index, info=info, hint=hint)
            sys.exit(2)

    def __validate_double_len_token_symbols(self, line_index, token_index, token):
        if token[0] == '-':
            if token[1] in ['I', 'O', 'P']:
                return True
            else:
                info = f"TOKEN_ERROR_RULE_02: Invalid token: {token}"
                hint = "Only I, O, or P can follow after the - (hyphen)."
                self.__print_syntax_error(line_num=line_index, info=info, hint=hint)
                sys.exit(2)
        else:
            self.__validate_token_symbols(line_index, token)

    def __validate_token_symbols(self, line_index, token):
        for char in token:
            if char not in VALID_CHARS:
                info = f"TOKEN_ERROR_RULE_03: Invalid token: {token}"
                hint = f"Tokens cannot contain character: {char}"
                self.__print_syntax_error(line_num=line_index, info=info, hint=hint)
                sys.exit(2)

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
    def _validate_ocrd_lines(self):
        self.__validate_first_line(self.ocrd_lines[0])

        for line_index in range(1, len(self.ocrd_lines)-2):
            self.__validate_middle_line(line_index, self.ocrd_lines[line_index])

        self.__validate_last_line(len(self.ocrd_lines)-1, self.ocrd_lines[-1])

    def __validate_first_line(self, line):
        expected = ' '.join(['ocrd', 'process', BACKSLASH])
        got = ' '.join(line)
        if got != expected:
            hint = 'Single spaces are allowed between the tokens'
            self.__print_syntax_error(line_num=1, expected=expected, got=got, hint=hint)
            sys.exit(2)

    # Every line other than the first/last one.
    def __validate_middle_line(self, line_num, line):
        self.__validate_min_amount_of_tokens(line_num, line, min_amount=8)
        # get the first and last QM tokens of their expected indices
        first_qm_token = line[0]
        last_qm_token = line[-2]
        self.__validate_QM_tokens(line_num, first_qm_token, last_qm_token)
        backslash_token = line[-1]
        self.__validate_BACKSLASH_token(line_num, backslash_token)
        ocrd_processor_token = line[1]
        self.__validate_ocrd_processor_token(line_num, ocrd_processor_token)
        self.__validate_iop_tokens(line_num, line)

    def __validate_last_line(self, line_num, line):
        self.__validate_min_amount_of_tokens(line_num, line, min_amount=7)
        # get the first and last QM tokens of their expected indices
        first_qm_token = line[0]
        last_qm_token = line[-1]
        self.__validate_QM_tokens(line_num, first_qm_token, last_qm_token)
        ocrd_processor_token = line[1]
        self.__validate_ocrd_processor_token(line_num, ocrd_processor_token)
        self.__validate_iop_tokens(line_num, line)

    def __validate_min_amount_of_tokens(self, line_num, line, min_amount):
        if len(line) < min_amount:
            expected = f"At least {min_amount} tokens."
            got = f"{len(line)} tokens"
            hint = 'LINE_ERROR_RULE_02: Each line must have a processor call, an input file, and an output file'
            self.__print_syntax_error(line_num, expected=expected, got=got, hint=hint)
            sys.exit(2)

    def __validate_QM_tokens(self, line_num, first_qm_token, last_qm_token):
        if not first_qm_token == QM:
            hint = 'TLINE_ERROR_RULE_03: OCR-D commands must start with a quotation mark'
            self.__print_syntax_error(line_num, expected=QM, got=first_qm_token, hint=hint)
            sys.exit(2)
        if not last_qm_token == QM:
            hint = 'LINE_ERROR_RULE_11: OCR-D commands must end with a quotation mark'
            self.__print_syntax_error(line_num, expected=QM, got=last_qm_token, hint=hint)
            sys.exit(2)

    def __validate_BACKSLASH_token(self, line_num, token):
        if not token == BACKSLASH:
            hint = 'LINE_ERROR_RULE_12: OCR-D lines must end with a backslash, except the last line'
            self.__print_syntax_error(line_num, expected=BACKSLASH, got=token, hint=hint)
            sys.exit(2)

    def __validate_ocrd_processor_token(self, line_num, token):
        ocrd_processor = f"ocrd-{token}"
        if ocrd_processor not in OCRD_PROCESSORS:
            hint = 'LINE_ERROR_RULE_01: `ocrd process` is spelled incorrectly or does not exists'
            self.__print_syntax_error(line_num, expected='ocrd-*', got=ocrd_processor, hint=hint)
            sys.exit(2)

    # Validate input, output and parameter tokens and their arguments
    def __validate_iop_tokens(self, line_num, line):
        input_found = False  # track duplicate inputs
        output_found = False  # track duplicate outputs
        # track arguments passed to input/output/parameter
        # to avoid duplicate consideration of tokens
        processed_tokens = []

        for token_index in range(2, len(line)):
            current_token = line[token_index]

            if current_token in (QM, BACKSLASH):
                continue
            if current_token in processed_tokens:
                continue

            if current_token == '-I':
                if input_found:
                    self.__print_io_duplicate_error(line_num, token_index, current_token)
                next_token = line[token_index+1]
                self.__validate_input_token(line_num, token='-I', next_token=next_token)
                processed_tokens.append(next_token)
                input_found = True
            elif current_token == '-O':
                if output_found:
                    self.__print_io_duplicate_error(line_num, token_index, current_token)
                next_token = line[token_index+1]
                self.__validate_output_token(line_num, token='-O', next_token=next_token)
                processed_tokens.append(next_token)
                output_found = True
            elif current_token == '-P':
                next_token = line[token_index+1]
                next_token2 = line[token_index+2]
                self.__validate_parameter_token(line_num, token='-P', next_token=next_token, next_token2=next_token2)
                processed_tokens.append(next_token)
                processed_tokens.append(next_token2)
            else:
                info = "INPUT_OUTPUT_ERROR: Unknown token found: {current_token}"
                index = "{token_index}"
                self.__print_syntax_error(line_num, info=info, index=index)

    def __validate_input_token(self, line_num, token, next_token):
        self.__is_valid_follow_up_token(line_num, previous_token=token, token=next_token)

    def __validate_output_token(self, line_num, token, next_token):
        self.__is_valid_follow_up_token(line_num, previous_token=token, token=next_token)

    def __validate_parameter_token(self, line_num, token, next_token, next_token2):
        self.__is_valid_follow_up_token(line_num, previous_token=token, token=next_token, token2=next_token2)

    # Checks the token that comes after the previous token (either of these: -I, -O, or -P)
    def __is_valid_follow_up_token(self, line_num, previous_token, token, token2=None):
        # These tokens cannot be arguments passed to the previous_token
        forbidden_follow_ups = [QM, BACKSLASH, '-I', '-O', '-P']
        info = f"FOLLOW_UP_TOKEN_ERROR: Wrong or missing arguments to {previous_token}"

        if previous_token == '-P':
            hint = f"{previous_token} takes exactly 2 arguments."
        elif previous_token == '-I' or previous_token == '-O':
            hint = f"{previous_token} takes exactly 1 argument."
        else:
            hint = f"Check and correct {previous_token} arguments."

        if token in forbidden_follow_ups:
            self.__print_syntax_error(line_num, info=info, got=token, hint=hint)
            sys.exit(2)

        # Only the -P token has two follow up arguments
        if token2 and previous_token == '-P':
            if token2 in forbidden_follow_ups:
                self.__print_syntax_error(line_num, info=info, got=token2, hint=hint)
                sys.exit(2)

        return True

    def __print_io_duplicate_error(self, line_num, index, token):
        info = f"DUPLICATE_TOKENS_ERROR: Duplicate {token} found!"
        hint = f"Only a single {token} is allowed!"
        self.__print_syntax_error(line_num, info=info, index=index, hint=hint)

    def __print_syntax_error(self, line_num=None, info=None, line=None, index=None,
                            expected=None, got=None, hint=None, hint2=None):
        print("Syntax error!")
        if line_num:
            print(f"Invalid line number: {line_num}!")
        if info:
            print(f"Info: {info}.")
        if line:
            print(f"Line: {line}.")
        if index:
            print(f"Index: {index}.")
        if expected:
            print(f"Expected: '{expected}'.")
        if got:
            print(f"Got: '{got}'.")
        if hint:
            print(f"Hint: {hint}.")
        if hint2:
            print(f"Hint2: {hint2}.")

    def __print_ocrd_tokens(self):
        print(f"INFO: Lines in the ocrd file: {len(self.ocrd_lines)}")
        print("INFO: TOKENS ON LINES")
        for i in range (0, len(self.ocrd_lines)):
            print(f"ocrd_lines[{i}]: {self.ocrd_lines[i]}")
        print("INFO: TOKENS ON LINES END")
