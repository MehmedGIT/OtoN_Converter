from os.path import exists, isfile
import sys

from .constants import (
    BACKSLASH,
    COMMA,
    QM,
    VALID_CHARS
)
from .ocrd_processors_list import OCRD_PROCESSORS

__all__ = [
    "is_valid_file_path",
    "extract_file_lines",
    "extract_line_tokens",
    "extract_ocrd_command",
    "validate_first_line",
    "validate_middle_line",
    "validate_last_line",
    "print_syntax_error",
    "validate_single_len_token_symbols",
    "validate_double_len_token_symbols",
    "validate_token_symbols",
]

def is_valid_file_path(filepath):
    if not exists(filepath):
        print(f"OCR-D file: {filepath} does not exist!")
        sys.exit(2)
    if not isfile(filepath):
        print(f"OCR-D file: {filepath} is not a readable file!")
        sys.exit(2)
def extract_file_lines(filepath):
    ocrd_lines = []
    with open(filepath, mode='r', encoding='utf-8') as ocrd_file:
        for line in ocrd_file:
            ocrd_lines.append(line.strip().split(' '))
    return ocrd_lines
def extract_line_tokens(line):
    # Rule 1: Each QM and BACKSLASH is a separate token
    # Rule 2: Each ocrd-processor name is a separate token
    # Rule 3: Each -I, -O, and -P is a separate token

    tokens = []
    for element in line:
        if len(element) == 0:
            continue
        # Create separate tokens
        # for quotation marks
        if element.startswith(QM) and element.endswith(QM):
            tokens.append(QM)
            tokens.append(element[1:-1])
            tokens.append(QM)
        elif element.startswith(QM):
            tokens.append(QM)
            tokens.append(element[1:])
        elif element.endswith(QM):
            tokens.append(element[:-1])
            tokens.append(QM)
        else:
            tokens.append(element)

    return tokens
def extract_ocrd_command(line_tokens):
    ocrd_command = None

    first_qm_index = 0
    last_qm_index = 0

    for token_index in range(1, len(line_tokens)):
        curr_token = line_tokens[token_index]
        if curr_token == QM:
            last_qm_index = token_index
            break

    # Extract the processor field
    ocrd_processor = f"ocrd-{line_tokens[first_qm_index+1]}"
    # Append ocrd- as a prefix
    line_tokens[1] = ocrd_processor
    # Extract the ocr-d command without quotation marks
    ocrd_command = line_tokens[1:last_qm_index]

    return ocrd_command

def validate_first_line(line):
    expected = ' '.join(['ocrd', 'process', BACKSLASH])
    got = ' '.join(line)
    if got != expected:
        hint = 'Single spaces are allowed between the tokens'
        self.__print_syntax_error(line_num=1, expected=expected, got=got, hint=hint)
        sys.exit(2)
# Every line other than the first/last one.
def validate_middle_line(line_num, line):
    validate_min_amount_of_tokens(line_num, line, min_amount=8)
    # get the first and last QM tokens of their expected indices
    first_qm_token = line[0]
    last_qm_token = line[-2]
    validate_QM_tokens(line_num, first_qm_token, last_qm_token)
    backslash_token = line[-1]
    validate_BACKSLASH_token(line_num, backslash_token)
    ocrd_processor_token = line[1]
    validate_ocrd_processor_token(line_num, ocrd_processor_token)
    validate_iop_tokens(line_num, line)
def validate_last_line(line_num, line):
    validate_min_amount_of_tokens(line_num, line, min_amount=7)
    # get the first and last QM tokens of their expected indices
    first_qm_token = line[0]
    last_qm_token = line[-1]
    validate_QM_tokens(line_num, first_qm_token, last_qm_token)
    ocrd_processor_token = line[1]
    validate_ocrd_processor_token(line_num, ocrd_processor_token)
    validate_iop_tokens(line_num, line)

def validate_min_amount_of_tokens(line_num, line, min_amount):
    if len(line) < min_amount:
        expected = f"At least {min_amount} tokens."
        got = f"{len(line)} tokens"
        info = 'LINE_ERROR_RULE_02: Not enough tokens.'
        hint = 'Each line must have a processor call, an input file, and an output file'
        print_syntax_error(line_num, info=info, expected=expected, got=got, hint=hint)
        sys.exit(2)
def validate_QM_tokens(line_num, first_qm_token, last_qm_token):
    if not first_qm_token == QM:
        info = 'LINE_ERROR_RULE_03: Wrong start of the OCR-D command'
        hint = 'OCR-D commands must start with a quotation mark'
        print_syntax_error(line_num, info=info, expected=QM, got=first_qm_token, hint=hint)
        sys.exit(2)
    if not last_qm_token == QM:
        info = 'LINE_ERROR_RULE_11: Wrong end of the OCR-D command'
        hint = 'OCR-D commands must end with a quotation mark'
        print_syntax_error(line_num, info=info, expected=QM, got=last_qm_token, hint=hint)
        sys.exit(2)
def validate_BACKSLASH_token(line_num, token):
    if not token == BACKSLASH:
        info = 'LINE_ERROR_RULE_12: Missing backslash at the end of line'
        hint = 'OCR-D lines must end with a backslash, except the last line'
        print_syntax_error(line_num, info=info, expected=BACKSLASH, got=token, hint=hint)
        sys.exit(2)
def validate_ocrd_processor_token(line_num, token):
    ocrd_processor = f"ocrd-{token}"
    if ocrd_processor not in OCRD_PROCESSORS:
        info = f'LINE_ERROR_RULE_01: Unknown processor {token}'
        hint = 'Processor is spelled incorrectly or does not exists'
        print_syntax_error(line_num, info=info, expected='ocrd-*', got=ocrd_processor, hint=hint)
        sys.exit(2)

# Validate input, output and parameter tokens and their arguments
def validate_iop_tokens(line_num, line):
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
                print_io_duplicate_error(line_num, token_index, current_token)
            next_token = line[token_index+1]
            validate_input_token(line_num, token='-I', next_token=next_token)
            processed_tokens.append(next_token)
            input_found = True
        elif current_token == '-O':
            if output_found:
                print_io_duplicate_error(line_num, token_index, current_token)
            next_token = line[token_index+1]
            validate_output_token(line_num, token='-O', next_token=next_token)
            processed_tokens.append(next_token)
            output_found = True
        elif current_token == '-P':
            next_token = line[token_index+1]
            next_token2 = line[token_index+2]
            validate_parameter_token(line_num, token='-P', next_token=next_token, next_token2=next_token2)
            processed_tokens.append(next_token)
            processed_tokens.append(next_token2)
        else:
            info = f"UNEXPECTED_TOKEN_ERROR: Unknown token found: {current_token}"
            index = f"{token_index}"
            print_syntax_error(line_num, info=info, index=index)
def validate_input_token(line_num, token, next_token):
    is_valid_follow_up_token(line_num, previous_token=token, token=next_token)
def validate_output_token(line_num, token, next_token):
    is_valid_follow_up_token(line_num, previous_token=token, token=next_token)
def validate_parameter_token(line_num, token, next_token, next_token2):
    is_valid_follow_up_token(line_num, previous_token=token, token=next_token, token2=next_token2)
# Checks the token that comes after the previous token (either of these: -I, -O, or -P)
def is_valid_follow_up_token(line_num, previous_token, token, token2=None):
    # These tokens cannot be arguments passed to the previous_token
    forbidden_follow_ups = [QM, BACKSLASH, '-I', '-O', '-P']
    info = f"ARGUMENT_TOKEN_ERROR: Wrong or missing arguments to {previous_token}"

    if previous_token == '-P':
        hint = f"{previous_token} takes exactly 2 arguments."
    elif previous_token == '-I' or previous_token == '-O':
        hint = f"{previous_token} takes exactly 1 argument."
    else:
        hint = f"Check and correct {previous_token} arguments."

    if token in forbidden_follow_ups:
        print_syntax_error(line_num, info=info, got=token, hint=hint)
        sys.exit(2)

    # Only the -P token has two follow up arguments
    if token2 and previous_token == '-P':
        if token2 in forbidden_follow_ups:
            print_syntax_error(line_num, info=info, got=token2, hint=hint)
            sys.exit(2)

    return True


def validate_single_len_token_symbols(line_index, token_index, token):
    if token in (QM, BACKSLASH):
        return True
    else:
        info = f"TOKEN_SYMBOL_ERROR_RULE_01: Invalid token: {token}"
        hint = "Single len tokens can be either a quotation mark or a backslash."
        print_syntax_error(line_num=line_index, info=info, hint=hint)
        sys.exit(2)
def validate_double_len_token_symbols(line_index, token_index, token):
    if token[0] == '-':
        if token[1] in ['I', 'O', 'P']:
            return True
        else:
            info = f"TOKEN_SYMBOL_ERROR_RULE_02: Invalid token: {token}"
            hint = "Only I, O, or P can follow after the - (hyphen)."
            print_syntax_error(line_num=line_index, info=info, hint=hint)
            sys.exit(2)
    else:
        validate_token_symbols(line_index, token)
# TODO: This is too complex, refactor it! Pain for others to read and understand...
def validate_token_symbols(line_index, token):
    for char in token:
        if char not in VALID_CHARS:
            # check if the comma char is a separation for input/output folders
            if char == COMMA:
                folder_tokens = token.split(COMMA)
                for folder_token in folder_tokens:
                    if not validate_token_symbols(line_index, folder_token):
                        info = f"TOKEN_SYMBOL_ERROR_RULE_03: Invalid token: {token}"
                        hint = f"Tokens cannot contain character: {char}"
                        print_syntax_error(line_num=line_index, info=info, hint=hint)
                        sys.exit(2)
            else:
                info = f"TOKEN_SYMBOL_ERROR_RULE_03: Invalid token: {token}"
                hint = f"Tokens cannot contain character: {char}"
                print_syntax_error(line_num=line_index, info=info, hint=hint)
                sys.exit(2)
     
    return True

def print_io_duplicate_error(line_num, index, token):
    info = f"DUPLICATE_TOKEN_ERROR: Duplicate {token} found!"
    hint = f"Only a single {token} is allowed!"
    print_syntax_error(line_num, info=info, index=index, hint=hint)

def print_syntax_error(line_num=None, info=None, line=None, index=None, expected=None, got=None, hint=None, hint2=None):
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