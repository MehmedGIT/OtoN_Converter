from .models import NextflowScript
from .validators.ocrd_validator import OCRDValidator
from .validators.validator_utils import validate_file_path
from .utils import (
    extract_file_lines,
    extract_ocrd_tokens,
    extract_ocrd_commands
)


class Converter:
    def __init__(self):
        pass

    @staticmethod
    def convert_OtoN(input_path: str, output_path: str, dockerized: bool = False):
        ocrd_validator = OCRDValidator()
        validate_file_path(input_path)
        file_lines = extract_file_lines(input_path)
        ocrd_lines = extract_ocrd_tokens(file_lines)
        ocrd_validator.validate_ocrd_lines(ocrd_lines)
        ocrd_commands = extract_ocrd_commands(ocrd_lines)

        nextflow_script = NextflowScript()
        nextflow_script.build_parameters(dockerized)
        nf_processes = nextflow_script.build_nextflow_processes(ocrd_commands, dockerized)
        nextflow_script.build_main_workflow(nf_processes)
        nextflow_script.produce_nextflow_file(output_path)
