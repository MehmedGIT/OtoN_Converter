from .constants import (
    BRACKETS,
    SPACE_AMOUNT
)

class Nextflow_Workflow:
    def __init__(self, workflow_name, nf_processes):
        self.workflow_name = workflow_name
        # Nextflow processes
        self.nf_processes = nf_processes

    def file_representation(self):
        representation = f'workflow {BRACKETS[0]}\n'
        representation += f'{SPACE_AMOUNT}{self.workflow_name}:\n'

        previous_nfp = None
        # TODO: Further refactoring needed - params.mets should be dynamic
        for nfp in self.nf_processes:
            if previous_nfp is None:
                representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{nfp[0]}(params.mets, {nfp[1]}, {nfp[2]})\n'
            else:
                representation += f'{SPACE_AMOUNT}{SPACE_AMOUNT}{nfp[0]}(params.mets, {previous_nfp}.out, {nfp[2]})\n'
            previous_nfp = nfp[0]

        representation += f'{BRACKETS[1]}\n'
        representation += '\n'

        return representation
