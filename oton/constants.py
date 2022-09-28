from pkg_resources import resource_filename
from string import ascii_letters, digits

__all__ = [
    "BACKSLASH",
    "BRACKETS",
    "LF",
    "QM",
    "SPACE",
    "TAB",
    "TOML_CONFIG",
    "VALID_CHARS",

    "DSL2",
    "IN_DIR",
    "OUT_DIR",
    "IN_DIR_PH",
    "OUT_DIR_PH",
    "DOCKER_PREFIX"
]

# SYMBOLS
BACKSLASH = '\\'
BRACKETS = '{}'
LF = '\n'
QM = '"' # Quotation Mark
SPACE = ' '
TAB = '\t'

TOML_CONFIG: str = resource_filename(__name__, 'config.toml')

# Valid characters to be used in the ocrd file
VALID_CHARS: str = f'-_.{ascii_letters}{digits}'

# NEXTFLOW RELATED
DSL2 = 'nextflow.enable.dsl = 2'
# input/output dirs
IN_DIR = 'input_dir'
OUT_DIR = 'output_dir'
# input/output dirs placeholders
IN_DIR_PH = f'${BRACKETS[0]}{IN_DIR}{BRACKETS[1]}'
OUT_DIR_PH = f'${BRACKETS[0]}{OUT_DIR}{BRACKETS[1]}'
# Docker command
DOCKER_PREFIX = f'${BRACKETS[0]}params.docker_command{BRACKETS[1]}'