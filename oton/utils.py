import logging
from typing import List

from validators.constants import (
    QM
)
from .constants import (
    OTON_LOG_FORMAT,
    OTON_LOG_LEVEL
)


__all__ = [
    "extract_file_lines",
    "extract_line_tokens",
    "extract_ocrd_tokens",
    "extract_ocrd_commands",
    "extract_ocrd_command",
]


logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(OTON_LOG_LEVEL))
logging.basicConfig(format=OTON_LOG_FORMAT)


# TODO: Some of these functions
# could and should be further refined


def extract_file_lines(filepath: str):
    file_lines = []
    with open(filepath, mode='r', encoding='utf-8') as ocrd_file:
        for line in ocrd_file:
            line_tokens_list: List[str] = line.strip().split(' ')
            if len(line_tokens_list) > 0:
                file_lines.append(line_tokens_list)
                logger.debug(line_tokens_list)
    return file_lines


def extract_ocrd_tokens(ocrd_lines):
    ocrd_tokens = []
    for line in ocrd_lines:
        curr_line_tokens = extract_line_tokens(line)
        if len(curr_line_tokens) > 0:
            ocrd_tokens.append(curr_line_tokens)
    return ocrd_tokens


def extract_line_tokens(line) -> List[str]:
    # Rule 1: Each QM and BACKSLASH is a separate token
    # Rule 2: Each ocrd-processor name is a separate token
    # Rule 3: Each -I, -O, and -P is a separate token
    line_tokens = []
    for element in line:
        if len(element) == 0:
            continue
        if element.startswith(QM) and element.endswith(QM):
            line_tokens.append(QM)
            line_tokens.append(element[1:-1])
            line_tokens.append(QM)
        elif element.startswith(QM):
            line_tokens.append(QM)
            line_tokens.append(element[1:])
        elif element.endswith(QM):
            line_tokens.append(element[:-1])
            line_tokens.append(QM)
        else:
            line_tokens.append(element)
    logger.debug(line_tokens)
    return line_tokens


def extract_ocrd_commands(ocrd_lines) -> List[List[str]]:
    ocrd_commands = []
    for line_index in range(1, len(ocrd_lines)):
        ocrd_command = extract_ocrd_command(ocrd_lines[line_index])
        ocrd_commands.append(ocrd_command)
    return ocrd_commands


def extract_ocrd_command(line_tokens) -> List[str]:
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
    logger.debug(ocrd_command)
    return ocrd_command
