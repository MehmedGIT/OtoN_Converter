from .ocrd_validator import OCRD_Validator
from .nextflow_script import Nextflow_Script

class Converter:
    def __init__(self):
        pass

    def convert_OtoN(self, input_path, output_path, dockerized=False):
        ocrd_validator = OCRD_Validator()
        ocrd_lines = ocrd_validator.extract_and_validate_ocrd_file(input_path)
        ocrd_commands = ocrd_validator.extract_ocrd_commands(ocrd_lines)

        nextflow_script = Nextflow_Script()
        nextflow_script.build_parameters(dockerized)
        nf_processes = nextflow_script.build_nextflow_processes(ocrd_commands, dockerized)
        nextflow_script.build_main_workflow(nf_processes)
        nextflow_script.produce_nextflow_file(output_path)
