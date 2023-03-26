import logging
from typing import List

from ..validators.ocrd_validator import ProcessorCallArguments
from ..constants import (
    OTON_LOG_FORMAT,
    OTON_LOG_LEVEL,
)
from .constants import (
    DIR_IN,
    DIR_OUT,
    METS_FILE,

    REPR_DSL2,
    REPR_DOCKER_COMMAND,
    REPR_DOCKER_IMAGE,
    REPR_DOCKER_MODELS,
    REPR_DOCKER_MODELS_DIR,
    REPR_DOCKER_PWD,
    REPR_DOCKER_VOLUME,
    REPR_METS_PATH,
    REPR_MODELS_PATH,
    REPR_VENV_PATH,
    REPR_WORKSPACE_PATH
)
from .nf_block_process import NextflowBlockProcess
from .nf_block_workflow import NextflowBlockWorkflow


class NextflowFileExecutable:
    def __init__(self):
        self.nf_lines = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.getLevelName(OTON_LOG_LEVEL))
        logging.basicConfig(format=OTON_LOG_FORMAT)

    def build_parameters(self, dockerized: bool = False):
        self.nf_lines.append(REPR_DSL2)
        self.nf_lines.append('')

        self.nf_lines.append(REPR_WORKSPACE_PATH)
        self.nf_lines.append(REPR_METS_PATH)

        if dockerized:
            self.nf_lines.append(REPR_DOCKER_PWD)
            self.nf_lines.append(REPR_DOCKER_VOLUME)
            self.nf_lines.append(REPR_DOCKER_MODELS_DIR)
            self.nf_lines.append(REPR_MODELS_PATH)
            self.nf_lines.append(REPR_DOCKER_MODELS)
            self.nf_lines.append(REPR_DOCKER_IMAGE)
            self.nf_lines.append(REPR_DOCKER_COMMAND)
        else:
            self.nf_lines.append(REPR_VENV_PATH)

        self.nf_lines.append('')

    def build_nextflow_processes(self, ocrd_processor: List[ProcessorCallArguments], dockerized: bool = False) -> List[str]:
        nf_processes = []

        index = 0
        for processor in ocrd_processor:
            nf_process_block = NextflowBlockProcess(processor, index, dockerized)
            nf_process_block.add_directive('maxForks 1')
            nf_process_block.add_input_param(f'path {METS_FILE}')
            nf_process_block.add_input_param(f'val {DIR_IN}')
            nf_process_block.add_input_param(f'val {DIR_OUT}')
            nf_process_block.add_output_param(f'path {METS_FILE}')
            self.nf_lines.append(nf_process_block.file_representation())

            # This list is used when building the workflow
            nf_processes.append(nf_process_block.repr_in_workflow)
            self.logger.info(f"Successfully created Nextflow Process: {nf_process_block.nf_process_name}")
            index += 1

        return nf_processes

    def build_main_workflow(self, nf_processes: List[str]):
        nf_workflow_block = NextflowBlockWorkflow("main", nf_processes)
        self.nf_lines.append(nf_workflow_block.file_representation())

    def produce_nextflow_file(self, output_path: str):
        # Write Nextflow line tokens to an output file
        with open(output_path, mode='w', encoding='utf-8') as nextflow_file:
            for nextflow_line in self.nf_lines:
                nextflow_file.write(f'{nextflow_line}\n')
