from .ocrd_validator import OCRDValidator
from oton.models.nextflow_script import NextflowScript
from .utils import (
    validate_file_path,
    extract_file_lines,
)


class Converter:
    def __init__(self):
        pass

    def convert_OtoN(self, input_path, output_path, dockerized=False):
        ocrd_validator = OCRDValidator()
        validate_file_path(input_path)
        file_lines = extract_file_lines(input_path)
        ocrd_lines = ocrd_validator.extract_ocrd_tokens(file_lines)
        ocrd_validator.validate_ocrd_token_symbols(ocrd_lines)
        ocrd_validator.validate_ocrd_lines(ocrd_lines)
        ocrd_commands = ocrd_validator.extract_ocrd_commands(ocrd_lines)

        nextflow_script = NextflowScript()
        nextflow_script.build_parameters(dockerized)
        nf_processes = nextflow_script.build_nextflow_processes(ocrd_commands, dockerized)
        nextflow_script.build_main_workflow(nf_processes)
        nextflow_script.produce_nextflow_file(output_path)
