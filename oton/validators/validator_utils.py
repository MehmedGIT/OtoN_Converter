import logging
from os.path import exists, isfile
from typing import List, Tuple

from ..constants import (
    OTON_LOG_LEVEL,
    OTON_LOG_FORMAT
)
from .constants import (
    BACKSLASH,
    COMMA,
    QM,
    VALID_CHARS
)

__all__ = [
    "validate_file_path",
    "validate_ocrd_process_command",
    "validate_line_token_symbols",
    "validate_iop_tokens"
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(OTON_LOG_LEVEL))
logging.basicConfig(format=OTON_LOG_FORMAT)


def validate_file_path(filepath: str):
    if not exists(filepath):
        raise ValueError(f"{filepath} does not exist!")
    if not isfile(filepath):
        raise ValueError(f"{filepath} is not a readable file!")
    logger.debug(f"Input file path validated: {filepath}")


def validate_ocrd_process_command(line: str):
    expected = 'ocrd process'
    if line != expected:
        raise ValueError(f"Invalid first line. Expected: '{expected}', got: '{line}'")
    logger.info(f"Line 0 was validated successfully")


# Validate input, output and parameter tokens and their arguments
def validate_iop_tokens(line_num: int, line: List[str]) -> Tuple[str, str, dict]:
    input_already_found = False  # Track duplicate inputs
    output_already_found = False  # Track duplicate outputs
    # Track arguments passed to input/output/parameter
    # to avoid duplicate consideration of tokens
    processed_tokens = []
    return_input_str = ""
    return_output_str = ""
    return_params = {}

    for token_index in range(0, len(line)):
        current_token = line[token_index]
        logger.debug(f"Trying to validate token on line {line_num}: {current_token}")
        if current_token in (QM, BACKSLASH):
            logger.debug(f"Token does not need validation: {current_token}")
            continue
        if current_token in processed_tokens:
            logger.debug(f"Token already validated: {current_token}")
            continue
        if current_token == '-I':
            if input_already_found:
                raise ValueError(f"Only one such token is allowed on line {line_num}: {current_token}")
            try:
                next_token = line[token_index + 1]
            except ValueError:
                raise ValueError(f"On line {line_num}, no follow-up token for token: {current_token}")
            validate_iop_follow_up_tokens(line_num, previous_token=current_token, next_token=next_token)
            processed_tokens.append(next_token)
            input_already_found = True
            logger.debug(f"Input token pair validated: {current_token} {next_token}")
            return_input_str = next_token
        elif current_token == '-O':
            if output_already_found:
                raise ValueError(f"Only one such token is allowed on line {line_num}: {current_token}")
            try:
                next_token = line[token_index + 1]
            except ValueError:
                raise ValueError(f"On line {line_num}, no follow-up token for token: {current_token}")
            validate_iop_follow_up_tokens(line_num, previous_token=current_token, next_token=next_token)
            processed_tokens.append(next_token)
            output_already_found = True
            logger.debug(f"Output token pair validated: {current_token} {next_token}")
            return_output_str = next_token
        elif current_token == '-P':
            try:
                next_token = line[token_index + 1]
                next_token2 = line[token_index + 2]
            except ValueError:
                raise ValueError(f"On line {line_num}, no follow-up tokens for token: {current_token}")
            validate_iop_follow_up_tokens(line_num, previous_token=current_token,
                                          next_token=next_token, next_token2=next_token2)
            processed_tokens.append(next_token)
            processed_tokens.append(next_token2)
            return_params[next_token] = next_token2
            logger.debug(f"Parameter tokens validated: {current_token} {next_token} {next_token2}")
        else:
            raise ValueError(f"Unexpected token found on line {line_num}: {current_token}")

    if not input_already_found:
        raise ValueError(f"On line {line_num}, missing input token: -I")

    return return_input_str, return_output_str, return_params


def validate_iop_follow_up_tokens(line_num: int, previous_token: str, next_token: str, next_token2: str = None):
    # Checks the next token/s that come/s after the previous token (either of these: -I, -O, or -P)
    forbidden_follow_ups = [COMMA, QM, BACKSLASH, '-I', '-O', '-P']

    if next_token in forbidden_follow_ups:
        raise ValueError(f"On line {line_num}, {previous_token} got forbidden follow-up token: {next_token}")
    else:
        logger.debug(f"On line {line_num}, {previous_token} got as follow-up: {next_token}")

    if next_token2:
        # Only a -P token has a second follow-up argument
        if previous_token == '-P':
            if next_token2 in forbidden_follow_ups:
                raise ValueError(f"On line {line_num}, {previous_token} got forbidden second follow-up token: {next_token2}")
            else:
                logger.debug(f"On line {line_num}, {previous_token} got as a second follow-up: {next_token2}")
        else:
            raise ValueError(f"On line {line_num}, unexpected {previous_token} got follow-up token: {next_token2}")


def validate_line_token_symbols(line_index: int, line: List[str]):
    for token_index in range(0, len(line)):
        current_token = line[token_index]
        logger.debug(f"Line {line_index}, token validation: {current_token}")
        if len(current_token) == 1:
            if current_token not in (QM, BACKSLASH):
                raise ValueError(f"Invalid token on line {line_index}: {current_token}")
        elif len(current_token) == 2:
            if current_token[0] == '-' and current_token[1] not in ['I', 'O', 'P']:
                raise ValueError(f"Invalid token on line {line_index}: {current_token}")
            else:
                validate_token(current_token)
        else:
            # Check if the comma char is a separation for input/output folders
            if COMMA in current_token:
                folder_tokens: List[str] = current_token.split(COMMA)
                for folder_token in folder_tokens:
                    validate_token(folder_token)
            else:
                validate_token(current_token)
        logger.debug(f"Line {line_index}, token validated: {current_token}")


def validate_token(token: str) -> None:
    for char in token:
        if char not in VALID_CHARS:
            raise ValueError(f"Invalid char: {char} in token: {token}")
