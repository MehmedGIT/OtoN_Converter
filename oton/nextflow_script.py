from .nextflow_process import Nextflow_Process
from .nextflow_workflow import Nextflow_Workflow
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

class Nextflow_Script:
    def __init__(self):
        self.nf_lines = []

    def build_parameters(self, dockerized=False):
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

    def build_nextflow_processes(self, ocrd_commands, dockerized=False):
        nf_processes = []

        for ocrd_command in ocrd_commands:
            index_pos = ocrd_commands.index(ocrd_command)
            nextflow_process = Nextflow_Process(ocrd_command, index_pos, dockerized)
            nextflow_process.add_directive('maxForks 1')
            nextflow_process.add_input_param(f'path {METS_FILE}')
            nextflow_process.add_input_param(f'val {DIR_IN}')
            nextflow_process.add_input_param(f'val {DIR_OUT}')
            nextflow_process.add_output_param(f'val {DIR_OUT}')
            self.nf_lines.append(nextflow_process.file_representation())

            # This list is used when building the workflow
            nf_processes.append(nextflow_process.repr_in_workflow)

        return nf_processes

    def build_main_workflow(self, nf_processes):
        nextflow_workflow = Nextflow_Workflow("main", nf_processes)
        self.nf_lines.append(nextflow_workflow.file_representation())

    def produce_nextflow_file(self, output_path):
        # self.__print_nextflow_tokens()
        # Write Nextflow line tokens to an output file
        with open(output_path, mode='w', encoding='utf-8') as nextflow_file:
            for token_line in self.nf_lines:
                nextflow_file.write(f'{token_line}\n')

    def __print_nextflow_tokens(self):
        print(f'INFO: lines in the nextflow file: {len(self.nf_lines)}')
        print('INFO: TOKENS ON LINES')
        for i in range (0, len(self.nf_lines)):
            print(f'nf_lines[{i}]: {self.nf_lines[i]}')
        print('INFO: TOKENS ON LINES END')
