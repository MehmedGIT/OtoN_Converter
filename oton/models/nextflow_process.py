import logging
from typing import List
from ..constants import (
    SPACES,

    PH_DIR_IN,
    PH_DIR_OUT,
    PH_DOCKER_COMMAND,
    PH_VENV_PATH,
    OTON_LOG_LEVEL,
    OTON_LOG_FORMAT
)


class NextflowProcess:
    def __init__(self, ocrd_command, index_pos: int, dockerized: bool = False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.getLevelName(OTON_LOG_LEVEL))
        logging.basicConfig(format=OTON_LOG_FORMAT)

        self.dockerized = dockerized
        self.process_name = self._extract_process_name(ocrd_command[0]) + "_" + str(index_pos)
        in_index, out_index = self._find_io_files_value_indices(ocrd_command)
        self.ocrd_cmd_input, self.ocrd_cmd_output = self._find_io_files_values(ocrd_command, in_index, out_index)
        self.repr_in_workflow = [self.process_name, self.ocrd_cmd_input, self.ocrd_cmd_output]
        ocrd_command = self._replace_io_files_with_placeholders(ocrd_command, in_index, out_index)
        self.ocrd_command_bash = ' '.join(ocrd_command)
        self.directives = []
        self.input_params = []
        self.output_params = []

    def file_representation(self):
        representation = f'process {self.process_name}' + ' {\n'

        for directive in self.directives:
            representation += f'{SPACES}{directive}\n'
        representation += '\n'

        representation += f'{SPACES}input:\n'
        for input_param in self.input_params:
            representation += f'{SPACES}{SPACES}{input_param}\n'
        representation += '\n'

        representation += f'{SPACES}output:\n'
        for output_param in self.output_params:
            representation += f'{SPACES}{SPACES}{output_param}\n'
        representation += '\n'

        representation += f'{SPACES}script:\n'
        representation += f'{SPACES}{SPACES}"""\n'
        if self.dockerized:
            representation += f'{SPACES}{SPACES}{PH_DOCKER_COMMAND} {self.ocrd_command_bash}\n'
        else:
            representation += f'{SPACES}{SPACES}source "{PH_VENV_PATH}"\n'
            representation += f'{SPACES}{SPACES}{self.ocrd_command_bash}\n'
            representation += f'{SPACES}{SPACES}deactivate\n'
        representation += f'{SPACES}{SPACES}"""\n'

        representation += '}\n'

        self.logger.debug(f"\n{representation}")
        return representation

    def add_directive(self, directive: str):
        self.directives.append(directive)

    def add_input_param(self, parameter: str):
        self.input_params.append(parameter)

    def add_output_param(self, parameter: str):
        self.output_params.append(parameter)

    def _extract_process_name(self, ocrd_processor_name: str):
        process_name = ocrd_processor_name.replace('-', '_')
        self.logger.debug(f"\nGenerating NF process name: {ocrd_processor_name} -> {process_name}")
        return process_name

    def _find_io_files_value_indices(self, ocrd_command: List[str]):
        input_index = ocrd_command.index('-I') + 1
        output_index = ocrd_command.index('-O') + 1
        return input_index, output_index

    def _find_io_files_values(self, ocrd_command: List[str], in_index: int, out_index: int):
        ocrd_command_input = f'"{ocrd_command[in_index]}"'
        ocrd_command_output = f'"{ocrd_command[out_index]}"'
        return ocrd_command_input, ocrd_command_output

    def _replace_io_files_with_placeholders(self, ocrd_command: List[str], input_index: int, output_index: int):
        self.logger.debug(f"Replacing: {ocrd_command[input_index]} with {PH_DIR_IN}")
        ocrd_command[input_index] = PH_DIR_IN
        self.logger.debug(f"Replacing: {ocrd_command[output_index]} with {PH_DIR_OUT}")
        ocrd_command[output_index] = PH_DIR_OUT
        return ocrd_command
