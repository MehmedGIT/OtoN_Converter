from .constants import (
    SPACES,

    PARAMS_KEY_METS_PATH
)

class Nextflow_Workflow:
    def __init__(self, workflow_name, nf_processes):
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
                representation += f'{SPACES}{SPACES}{nfp[0]}({PARAMS_KEY_METS_PATH}, {previous_nfp}.out, {nfp[2]})\n'
            previous_nfp = nfp[0]

        representation += '}\n\n'

        return representation
