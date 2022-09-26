import sys
import getopt
from ocrd_validator import OCRD_Validator

# SYMBOLS
BRACKETS = '{}'
BACKSLASH = '\\'
# Quotation Mark
QM = '"'
TAB = '\t'
LF = '\n'
SPACE = ' '

# NEXTFLOW RELATED
DSL2 = 'nextflow.enable.dsl = 2'
# input/output dirs
IN_DIR = 'input_dir'
OUT_DIR = 'output_dir'
# input/output dirs placeholders
IN_DIR_PH = f'${BRACKETS[0]}{IN_DIR}{BRACKETS[1]}'
OUT_DIR_PH = f'${BRACKETS[0]}{OUT_DIR}{BRACKETS[1]}'

class Converter:
	def __init__(self):
		# Convention:
		# nf_lines holds the number of lines
		# of the output Nextflow file
		# for each line an inner list is created
		# to hold separate tokens of that line
		self.nf_lines = []

	def convert_OtoN(self, input_path, output_path):
		validator = OCRD_Validator()
		validator.validate_ocrd_file(input_path)
		ocrd_commands = validator.extract_ocrd_commands()

		# Nextflow script lines
		self.nf_lines = []

		# Rule 1: Create the default beginning of a Nextflow script
		self.__create_default_nextflow_beginning()

		# Rule 2: For each ocrd command (on each line) a separate Nextflow process is created
		nf_processes = self.__create_nextflow_processes(ocrd_commands)

		# Rule 3: Create the main workflow
		self.__create_main_workflow(nf_processes)

		self.__write_to_nextflow_file(output_path)
	
	def __create_default_nextflow_beginning(self):
		self.nf_lines.append(DSL2)
		self.nf_lines.append('')

		# The defaul pipeline parameters
		# Set _venv_path, _workspace_path, and _mets_path appropriately
		venv_path = '\$HOME/venv37-ocrd/bin/activate'
		params_venv = f'params.venv = {QM}{venv_path}{QM}'
		workspace_path = '$projectDir/ocrd-workspace/'
		params_workspace = f'params.workspace = {QM}{workspace_path}{QM}'
		mets_path = '$projectDir/ocrd-workspace/mets.xml'
		params_mets = f'params.mets = {QM}{mets_path}{QM}'

		self.nf_lines.append(params_venv)
		self.nf_lines.append(params_workspace)
		self.nf_lines.append(params_mets)
		self.nf_lines.append('')

	def __create_nextflow_processes(self, ocrd_commands):
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
			self.nf_lines.append(f'{TAB}source "${BRACKETS[0]}params.venv{BRACKETS[1]}"')
			self.nf_lines.append(f'{TAB}{oc_bash_str}')
			self.nf_lines.append(f'{TAB}deactivate')
			self.nf_lines.append(f'{TAB}"""')
			self.nf_lines.append(BRACKETS[1])
			self.nf_lines.append('')
			# This list is used inside the workflow section in Rule 3
			nf_processes.append([nf_process_name, oc_in, oc_out])

		return nf_processes
	
	def __create_main_workflow(self, nf_processes):
		self.nf_lines.append(f'workflow {BRACKETS[0]}')
		self.nf_lines.append(f'{TAB}main:')
		previous_nfp = None
		for nfp in nf_processes:
			if previous_nfp == None:
				self.nf_lines.append(f'{TAB}{TAB}{nfp[0]}(params.mets, {nfp[1]}, {nfp[2]})')
			else:
				self.nf_lines.append(f'{TAB}{TAB}{nfp[0]}(params.mets, {previous_nfp}.out, {nfp[2]})')
			previous_nfp = nfp[0]
		self.nf_lines.append(f'{BRACKETS[1]}')
	
	def __write_to_nextflow_file(self, output_path):
		# self.__print_nextflow_tokens()
		# Write Nextflow line tokens to an output file
		with open(output_path, mode='w') as nextflow_file:
			for token_line in self.nf_lines:
				nextflow_file.write(f'{token_line}\n')

	def _extract_nf_process_name(self, ocrd_processor_name):
		return f"{ocrd_processor_name.replace('-','_')}"

	def __print_nextflow_tokens(self):
		print(f"INFO: lines in the nextflow file: {len(self.nf_lines)}")
		print(f"INFO: TOKENS ON LINES")
		for i in range (0, len(self.nf_lines)):
			print(f"nf_lines[{i}]: {self.nf_lines[i]}")
		print(f"INFO: TOKENS ON LINES END")

def main(argv):
	input_path = ""
	output_path = ""

	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print("python3 converter.py -i <input_path> -o <output_path>")
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print("python3 converter.py -i <input_path> -o <output_path>")
			sys.exit()
		elif opt in ("-i", "--ifile"):
			input_path = arg
		elif opt in ("-o", "--ofile"):
			output_path = arg

	converter = Converter()
	print(f"OtoN> In: {input_path}")
	print(f"OtoN> Out: {output_path}")
	converter.convert_OtoN(input_path, output_path)

if __name__ == "__main__":
	main(sys.argv[1:])
