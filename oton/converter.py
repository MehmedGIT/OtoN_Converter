from .ocrd_validator import OCRD_Validator
from .nextflow import Nextflow

class Converter:
    def __init__(self):
        pass

    def convert_OtoN(self, input_path, output_path, dockerized=False):
        ocrd_validator = OCRD_Validator()
        ocrd_lines = ocrd_validator.extract_and_validate_ocrd_file(input_path)
        ocrd_commands = ocrd_validator.extract_ocrd_commands(ocrd_lines)

        nextflow = Nextflow()
        nextflow.build_default_beginning(dockerized)
        nf_processes = nextflow.build_nextflow_processes(ocrd_commands, dockerized)
        nextflow.build_main_workflow(nf_processes)
        nextflow.produce_nextflow_file(output_path)
