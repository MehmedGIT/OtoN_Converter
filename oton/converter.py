from .models import NextflowFileExecutable
from .validators.ocrd_validator import (
    OCRDValidator,
    OCRDValidatorWithCore
)


class Converter:
    def __init__(self):
        pass

    @staticmethod
    def convert_OtoN(input_path: str, output_path: str, dockerized: bool = False):
        validator = OCRDValidator()
        validator.validate(input_path)

        nf_file_executable = NextflowFileExecutable()
        nf_file_executable.build_parameters(dockerized)
        nf_processes = nf_file_executable.build_nextflow_processes(validator.processors, dockerized)
        nf_file_executable.build_main_workflow(nf_processes)
        nf_file_executable.produce_nextflow_file(output_path)

    @staticmethod
    def convert_OtoN_with_core(input_path: str, output_path: str, dockerized: bool = False):
        validator = OCRDValidatorWithCore()
        validator.validate(input_path)

        nf_file_executable = NextflowFileExecutable()
        nf_file_executable.build_parameters(dockerized)
        nf_processes = nf_file_executable.build_nextflow_processes(validator.processors, dockerized)
        nf_file_executable.build_main_workflow(nf_processes)
        nf_file_executable.produce_nextflow_file(output_path)