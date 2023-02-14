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
    "validate_file_path",
    "extract_file_lines",
    "extract_line_tokens",
    "extract_ocrd_command",
    "validate_first_line",
    "validate_middle_line",
    "validate_last_line",
    "validate_line_token_symbols",
    "print_syntax_error_and_exit",
]


# TODO: Some of these functions
# could and should be further refined

def validate_file_path(filepath):
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
    ocrd_processor = f"ocrd-{line_tokens[first_qm_index + 1]}"
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
        print_syntax_error_and_exit(line_num=1, expected=expected, got=got, hint=hint)


# Every line other than the first/last one.
def validate_middle_line(line_num, line):
    validate_min_amount_of_tokens(line_num, line, min_amount=8)
    validate_QM_tokens(line_num, line)
    validate_BACKSLASH_token(line_num, line)
    validate_ocrd_processor_token(line_num, line)
    validate_iop_tokens(line_num, line)


def validate_last_line(line_num, line):
    validate_min_amount_of_tokens(line_num, line, min_amount=7)
    validate_QM_tokens(line_num, line, is_last_line=True)
    validate_ocrd_processor_token(line_num, line)
    validate_iop_tokens(line_num, line)


def validate_min_amount_of_tokens(line_num, line, min_amount):
    if len(line) < min_amount:
        expected = f"At least {min_amount} tokens."
        got = f"{len(line)} tokens"
        info = 'LINE_ERROR_RULE_02: Not enough tokens.'
        hint = 'Each line must have a processor call, an input file, and an output file'
        print_syntax_error_and_exit(line_num, info=info, expected=expected, got=got, hint=hint)


def validate_QM_tokens(line_num, line, is_last_line=False):
    # get the first and last QM tokens of their expected indices
    first_qm_token = line[0]
    last_qm_token = line[-2]

    if is_last_line:
        last_qm_token = line[-1]

    if not first_qm_token == QM:
        info = 'LINE_ERROR_RULE_03: Wrong start of the OCR-D command'
        hint = 'OCR-D commands must start with a quotation mark'
        print_syntax_error_and_exit(line_num, info=info, expected=QM, got=first_qm_token, hint=hint)
    if not last_qm_token == QM:
        info = 'LINE_ERROR_RULE_11: Wrong end of the OCR-D command'
        hint = 'OCR-D commands must end with a quotation mark'
        print_syntax_error_and_exit(line_num, info=info, expected=QM, got=last_qm_token, hint=hint)


def validate_BACKSLASH_token(line_num, line):
    backslash_token = line[-1]
    if not backslash_token == BACKSLASH:
        info = 'LINE_ERROR_RULE_12: Missing backslash at the end of line'
        hint = 'OCR-D lines must end with a backslash, except the last line'
        print_syntax_error_and_exit(line_num, info=info, expected=BACKSLASH, got=backslash_token, hint=hint)


def validate_ocrd_processor_token(line_num, line):
    ocrd_processor_token = line[1]
    ocrd_processor = f"ocrd-{ocrd_processor_token}"
    if ocrd_processor not in OCRD_PROCESSORS:
        info = f'LINE_ERROR_RULE_01: Unknown processor {ocrd_processor_token}'
        hint = 'Processor is spelled incorrectly or does not exists'
        print_syntax_error_and_exit(line_num, info=info, expected='ocrd-*', got=ocrd_processor, hint=hint)


# Validate input, output and parameter tokens and their arguments
def validate_iop_tokens(line_num, line):
    input_already_found = False  # track duplicate inputs
    output_already_found = False  # track duplicate outputs
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
            if input_already_found:
                print_io_duplicate_error(line_num, token_index, current_token)
            next_token = line[token_index + 1]
            validate_iop_follow_up_tokens(line_num, token='-I', next_token=next_token)
            processed_tokens.append(next_token)
            input_found = True
        elif current_token == '-O':
            if output_already_found:
                print_io_duplicate_error(line_num, token_index, current_token)
            next_token = line[token_index + 1]
            validate_iop_follow_up_tokens(line_num, token='-O', next_token=next_token)
            processed_tokens.append(next_token)
            output_found = True
        elif current_token == '-P':
            next_token = line[token_index + 1]
            next_token2 = line[token_index + 2]
            validate_iop_follow_up_tokens(line_num, token='-P', next_token=next_token, next_token2=next_token2)
            processed_tokens.append(next_token)
            processed_tokens.append(next_token2)
        else:
            info = f"UNEXPECTED_TOKEN_ERROR: Unknown token found: {current_token}"
            index = f"{token_index}"
            print_syntax_error_and_exit(line_num, info=info, index=index)


def validate_iop_follow_up_tokens(line_num, token, next_token, next_token2=None):
    # Checks the token that comes after the previous token (either of these: -I, -O, or -P)
    is_valid_follow_up_token(line_num, previous_token=token, token=next_token, token2=next_token2)


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
        print_syntax_error_and_exit(line_num, info=info, got=token, hint=hint)

    # Only the -P token has two follow up arguments
    if token2 and previous_token == '-P':
        if token2 in forbidden_follow_ups:
            print_syntax_error_and_exit(line_num, info=info, got=token2, hint=hint)


def validate_line_token_symbols(line_index, line):
    for token_index in range(0, len(line)):
        current_token = line[token_index]
        if len(current_token) == 1:
            validate_single_len_token_symbols(line_index, token_index, current_token)
        elif len(current_token) == 2:
            validate_double_len_token_symbols(line_index, token_index, current_token)
        else:
            validate_other_len_token_symbols(line_index, current_token)


def validate_single_len_token_symbols(line_index, token_index, token):
    if not token in (QM, BACKSLASH):
        info = f"TOKEN_SYMBOL_ERROR_RULE_01: Invalid token: {token}"
        hint = "Single len tokens can be either a quotation mark or a backslash."
        print_syntax_error_and_exit(line_num=line_index, info=info, hint=hint)


def validate_double_len_token_symbols(line_index, token_index, token):
    if token[0] == '-' and not token[1] in ['I', 'O', 'P']:
        info = f"TOKEN_SYMBOL_ERROR_RULE_02: Invalid token: {token}"
        hint = "Only I, O, or P can follow after the - (hyphen)."
        print_syntax_error_and_exit(line_num=line_index, info=info, hint=hint)
    else:
        validate_other_len_token_symbols(line_index, token)


def validate_other_len_token_symbols(line_index, token):
    for char in token:
        # check if the comma char is a separation for input/output folders
        if char == COMMA:
            validate_folders_token_symbols(line_index, token)
        elif char not in VALID_CHARS:
            info = f"TOKEN_SYMBOL_ERROR_RULE_03: Invalid token: {token}"
            hint = f"Tokens cannot contain character: {char}"
            print_syntax_error_and_exit(line_num=line_index, info=info, hint=hint)


def validate_folders_token_symbols(line_index, token):
    folder_tokens = token.split(COMMA)
    for folder_token in folder_tokens:
        validate_other_len_token_symbols(line_index, folder_token)


def print_io_duplicate_error(line_num, index, token):
    info = f"DUPLICATE_TOKEN_ERROR: Duplicate {token} found!"
    hint = f"Only a single {token} is allowed!"
    print_syntax_error_and_exit(line_num, info=info, index=index, hint=hint)


def print_syntax_error_and_exit(line_num=None, info=None, line=None, index=None, expected=None, got=None, hint=None,
                                hint2=None):
    print("Syntax error!")
    if line: print(f"Line: {line}.")
    if line_num: print(f"Line number: {line_num}!")
    if index: print(f"Index: {index}.")
    if info: print(f"Info: {info}.")
    if expected: print(f"Expected: '{expected}'.")
    if got: print(f"Got: '{got}'.")
    if hint: print(f"Hint: {hint}.")
    if hint2: print(f"Hint2: {hint2}.")
    sys.exit(2)
