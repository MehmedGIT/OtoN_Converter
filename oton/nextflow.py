import tomli
from .constants import (
    BRACKETS,
    QM,
    TAB,
    TOML_CONFIG,

    DSL2,
    IN_DIR,
    OUT_DIR,
    IN_DIR_PH,
    OUT_DIR_PH,
    DOCKER_PREFIX
)

class Nextflow:
    def __init__(self):
        # Convention:
        # nf_lines holds the number of lines
        # of the output Nextflow file
        # for each line an inner list is created
        # to hold separate tokens of that line
        self.nf_lines = []

    def build_default_beginning(self, dockerized=False):
        self.nf_lines.append(DSL2)
        self.nf_lines.append('')

        # I do not really like what is happening here
        # TODO: Maybe a config file is not the right approach or should be modified.
        # The default pipeline parameters
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

        for oc in ocrd_commands:
            nf_process_name = self._extract_nf_process_name(oc[0])

            # Find the input/output parameters of the ocrd command
            in_index = oc.index('-I')+1
            out_index = oc.index('-O')+1
            oc_in = f'{QM}{oc[in_index]}{QM}'
            oc_out = f'{QM}{oc[out_index]}{QM}'

            # Replace the input/output parameters with their placeholders
            oc[in_index] = IN_DIR_PH
            oc[out_index] = OUT_DIR_PH
            # The bash string of the ocrd command
            oc_bash_str = ' '.join(oc)

            # Start building the current NF process
            self.nf_lines.append(f"process {nf_process_name} {BRACKETS[0]}")
            self.nf_lines.append(f"{TAB}maxForks 1")
            self.nf_lines.append('')
            self.nf_lines.append(f'{TAB}input:')
            self.nf_lines.append(f'{TAB}{TAB}path mets_file')
            self.nf_lines.append(f'{TAB}{TAB}val {IN_DIR}')
            self.nf_lines.append(f'{TAB}{TAB}val {OUT_DIR}')
            self.nf_lines.append('')
            self.nf_lines.append(f'{TAB}output:')
            self.nf_lines.append(f'{TAB}{TAB}val {OUT_DIR}')
            self.nf_lines.append('')
            self.nf_lines.append(f'{TAB}script:')
            self.nf_lines.append(f'{TAB}"""')
            if dockerized:
                self.nf_lines.append(f'{TAB}{DOCKER_PREFIX} {oc_bash_str}')
            else:
                self.nf_lines.append(f'{TAB}source "${BRACKETS[0]}params.venv{BRACKETS[1]}"')
                self.nf_lines.append(f'{TAB}{oc_bash_str}')
                self.nf_lines.append(f'{TAB}deactivate')
            self.nf_lines.append(f'{TAB}"""')
            self.nf_lines.append(BRACKETS[1])
            self.nf_lines.append('')
            # This list is used inside the workflow section in Rule 3
            nf_processes.append([nf_process_name, oc_in, oc_out])

        return nf_processes

    def build_main_workflow(self, nf_processes):
        self.nf_lines.append(f'workflow {BRACKETS[0]}')
        self.nf_lines.append(f'{TAB}main:')
        previous_nfp = None
        for nfp in nf_processes:
            if previous_nfp is None:
                self.nf_lines.append(f'{TAB}{TAB}{nfp[0]}(params.mets, {nfp[1]}, {nfp[2]})')
            else:
                self.nf_lines.append(f'{TAB}{TAB}{nfp[0]}(params.mets, {previous_nfp}.out, {nfp[2]})')
            previous_nfp = nfp[0]
        self.nf_lines.append(f'{BRACKETS[1]}')

    def produce_nextflow_file(self, output_path):
        # self.__print_nextflow_tokens()
        # Write Nextflow line tokens to an output file
        with open(output_path, mode='w', encoding='utf-8') as nextflow_file:
            for token_line in self.nf_lines:
                nextflow_file.write(f'{token_line}\n')

    def _extract_nf_process_name(self, ocrd_processor_name):
        return f"{ocrd_processor_name.replace('-','_')}"

    def __print_nextflow_tokens(self):
        print(f"INFO: lines in the nextflow file: {len(self.nf_lines)}")
        print("INFO: TOKENS ON LINES")
        for i in range (0, len(self.nf_lines)):
            print(f"nf_lines[{i}]: {self.nf_lines[i]}")
        print("INFO: TOKENS ON LINES END")