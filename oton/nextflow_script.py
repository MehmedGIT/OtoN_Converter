import tomli
from .nextflow_process import Nextflow_Process
from .nextflow_workflow import Nextflow_Workflow
from .constants import (
    QM,
    TOML_CONFIG,
    DSL2,

    IN_DIR,
    OUT_DIR,
    METS_FILE
)

class Nextflow_Script:
    def __init__(self):
        self.nf_lines = []

    def build_default_beginning(self, dockerized=False):
        self.nf_lines.append(DSL2)
        self.nf_lines.append('')

        # TODO: Further refactoring needed - this should happen inside the constants.py
        with open(TOML_CONFIG, mode='rb') as toml_f:
            config = tomli.load(toml_f)
            workspace_path = config['workspace_path']
            mets_path = config['mets_path']
            params_workspace = f'params.workspace = {QM}{workspace_path}{QM}'
            params_mets = f'params.mets = {QM}{mets_path}{QM}'
            self.nf_lines.append(params_workspace)
            self.nf_lines.append(params_mets)

            if dockerized:
                docker_pwd = config['docker_pwd']
                docker_volume = config['docker_volume']
                docker_image = config['docker_image']
                docker_command = config['docker_command']
                params_docker_pwd = f'params.docker_pwd = {QM}{docker_pwd}{QM}'
                params_docker_volume = f'params.docker_volume = {QM}{docker_volume}{QM}'
                params_docker_image = f'params.docker_image = {QM}{docker_image}{QM}'
                params_docker_command = f'params.docker_command = {QM}{docker_command}{QM}'
                self.nf_lines.append(params_docker_pwd)
                self.nf_lines.append(params_docker_volume)
                self.nf_lines.append(params_docker_image)
                self.nf_lines.append(params_docker_command)
            else:
                venv_path = config['venv_path']
                params_venv = f'params.venv = {QM}{venv_path}{QM}'
                self.nf_lines.append(params_venv)

        self.nf_lines.append('')

    def build_nextflow_processes(self, ocrd_commands, dockerized=False):
        nf_processes = []

        for ocrd_command in ocrd_commands:
            nextflow_process = Nextflow_Process(ocrd_command, dockerized)
            nextflow_process.add_directive('maxForks 1')
            nextflow_process.add_input_param(f'path {METS_FILE}')
            nextflow_process.add_input_param(f'val {IN_DIR}')
            nextflow_process.add_input_param(f'val {OUT_DIR}')
            nextflow_process.add_output_param(f'val {OUT_DIR}')
            self.nf_lines.append(nextflow_process.file_representation())

            # This list is used inside the workflow section in Rule 3
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