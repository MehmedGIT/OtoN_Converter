from .models import NextflowScript
from .validators.ocrd_validator import OCRDValidator


class Converter:
    def __init__(self):
        pass

    @staticmethod
    def convert_OtoN(input_path: str, output_path: str, dockerized: bool = False):
        validator = OCRDValidator()
        validator.validate(input_path)

        nextflow_script = NextflowScript()
        nextflow_script.build_parameters(dockerized)
        nf_processes = nextflow_script.build_nextflow_processes(validator.processors, dockerized)
        nextflow_script.build_main_workflow(nf_processes)
        nextflow_script.produce_nextflow_file(output_path)
