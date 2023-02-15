import logging
from ..constants import (
    SPACES,
    PARAMS_KEY_METS_PATH,
    OTON_LOG_LEVEL,
    OTON_LOG_FORMAT
)


class NextflowWorkflow:
    def __init__(self, workflow_name, nf_processes):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.getLevelName(OTON_LOG_LEVEL))
        logging.basicConfig(format=OTON_LOG_FORMAT)

        self.workflow_name = workflow_name
        # Nextflow processes
        self.nf_processes = nf_processes

    def file_representation(self):
        representation = 'workflow {\n'
        representation += f'{SPACES}{self.workflow_name}:\n'

        previous_nfp = None
        for nfp in self.nf_processes:
            if previous_nfp is None:
                representation += f'{SPACES}{SPACES}{nfp[0]}({PARAMS_KEY_METS_PATH}, {nfp[1]}, {nfp[2]})\n'
            else:
                representation += f'{SPACES}{SPACES}{nfp[0]}({previous_nfp}.out, {nfp[1]}, {nfp[2]})\n'
            previous_nfp = nfp[0]

        representation += '}\n\n'

        self.logger.debug(f"\n{representation}")
        self.logger.info(f"Successfully created Nextflow Workflow: {self.workflow_name}")
        return representation
