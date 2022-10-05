from .constants import (
    BRACKETS,
    QM,
    SPACE_AMOUNT,

    IN_DIR_PH,
    OUT_DIR_PH,
    DOCKER_PREFIX
)

class Nextflow_Process:
    # TODO: Further refactoring is needed here
    def __init__(self, ocrd_command, dockerized=False):
        self.dockerized = dockerized
        self.process_name = self._extract_process_name(ocrd_command[0])
        in_index, out_index = self._find_io_files_value_indices(ocrd_command)
        oc_in = f'{QM}{ocrd_command[in_index]}{QM}'
        oc_out = f'{QM}{ocrd_command[out_index]}{QM}'
        self.repr_in_workflow = [self.process_name, oc_in, oc_out]
        ocrd_command = self._replace_io_files_with_placeholders(ocrd_command, in_index, out_index)
        self.ocrd_command_bash = ' '.join(ocrd_command)
        self.directives = []
        self.input_params = []
        self.output_params = []
        
    def file_representation(self):
        representation = f'process {self.process_name} {BRACKETS[0]}\n'

        for directive in self.directives:
            representation += f'{SPACE_AMOUNT}{directive}\n'
        representation += '\n'

        representation += f'{SPACE_AMOUNT}input:\n'
        for input_param in self.input_params:
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{input_param}\n'
        representation += '\n'

        representation += f'{SPACE_AMOUNT}output:\n'
        for output_param in self.output_params:
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{output_param}\n'
        representation += '\n'

        representation += f'{SPACE_AMOUNT}script:\n'
        representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}"""\n'
        if self.dockerized:
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{DOCKER_PREFIX} {self.ocrd_command_bash}\n'
        else:
            # TODO: Further refactoring needed - params.venv should be dynamic
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}source "${BRACKETS[0]}params.venv{BRACKETS[1]}"\n'
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{self.ocrd_command_bash}\n'
            representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}deactivate\n'
        representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}"""\n'
        
        representation += f'{BRACKETS[1]}\n'

        return representation

    def add_directive(self, directive):
        self.directives.append(directive)

    def add_input_param(self, parameter):
        self.input_params.append(parameter)

    def add_output_param(self, parameter):
        self.output_params.append(parameter)

    def _extract_process_name(self, ocrd_processor_name):
        return f"{ocrd_processor_name.replace('-','_')}"

    def _find_io_files_value_indices(self, ocrd_command):
        return ocrd_command.index('-I')+1, ocrd_command.index('-O')+1

    def _replace_io_files_with_placeholders(self, ocrd_command, input_index, output_index):
        ocrd_command[input_index] = IN_DIR_PH
        ocrd_command[output_index] = OUT_DIR_PH
        return ocrd_command