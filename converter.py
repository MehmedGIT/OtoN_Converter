from os.path import exists, isfile
import string

# Valid characters to be used in the ocrd file
VALID_CHARS = f"-_.{string.ascii_letters}{string.digits}"

# All available processors.
# The list follows alphabetical order. 
# Source: https://ocr-d.de/en/workflows
OCRD_PROCESSORS = [
	'ocrd-anybaseocr-block-segmentation',
	'ocrd-anybaseocr-crop',
	'ocrd-anybaseocr-deskew',
	'ocrd-anybaseocr-dewarp',
	'ocrd-calamari-recognize',
	'ocrd-cis-align',
	'ocrd-cis-ocropy-binarize',
	'ocrd-cis-ocropy-clip',
	'ocrd-cis-ocropy-denoise',
	'ocrd-cis-ocropy-deskew',
	'ocrd-cis-ocropy-dewarp',
	'ocrd-cis-ocropy-resegment',
	'ocrd-cis-ocropy-segment',
	'ocrd-cis-postcorrect',
	'ocrd-cor-asv-ann-align',
	'ocrd-cor-asv-ann-evaluate',
	'ocrd-cor-asv-ann-process',
	'ocrd-detectron2-segment',
	'ocrd-dinglehopper',
	'ocrd-doxa-binarize',
	'ocrd-dummy',
	'ocrd-eynollah-segment',
	'ocrd-fileformat-transform',
	'ocrd-im6convert',
	'ocrd-olahd-client',
	'ocrd-olena-binarize',
	'ocrd-page-transform',
	'ocrd-page2tei',
	'ocrd-pagetopdf',
	'ocrd-pc-segmentation',
	'ocrd-preprocess-image',
	'ocrd-sbb-binarize',
	'ocrd-sbb-textline-detector',
	'ocrd-segment-evaluate',
	'ocrd-segment-extract-glyphs',
	'ocrd-segment-extract-lines',
	'ocrd-segment-extract-pages',
	'ocrd-segment-extract-regions',
	'ocrd-segment-extract-words',
	'ocrd-segment-from-coco',
	'ocrd-segment-from-masks',
	'ocrd-segment-project',
	'ocrd-segment-repair',
	'ocrd-segment-replace-original',
	'ocrd-segment-replace-page',
	'ocrd-skimage-binarize',
	'ocrd-skimage-normalize',
	'ocrd-skimage-denoise',
	'ocrd-skimage-denoise-raw',
	'ocrd-tesserocr-crop',
	'ocrd-tesserocr-deskew',
	'ocrd-tesserocr-fontshape',
	'ocrd-tesserocr-recognize',
	'ocrd-tesserocr-segment',
	'ocrd-tesserocr-segment-line',
	'ocrd-tesserocr-segment-region',
	'ocrd-tesserocr-segment-table',
	'ocrd-tesserocr-segment-word',
	'ocrd-typegroups-classifier'
]

class Converter:
	def __init__(self):
		# Convention:
		# ocrd_lines holds the number of lines
		# of the input ocrd file
		# for each line an inner list is created
		# to hold separate tokens of that line
		self.ocrd_lines = []
		# Convention:
		# nextflow_lines holds the number of lines
		# of the output nextflow file
		# for each line an inner list is created
		# to hold separate tokens of that line
		self.nextflow_lines = []

	def _print_ocrd_tokens(self):
		print(f"INFO: lines in the ocrd file: {len(self.ocrd_lines)}")
		print(f"INFO: TOKENS ON LINES")
		for i in range (0, len(self.ocrd_lines)):
			print(f"ocrd_lines[{i}]: {self.ocrd_lines[i]}")
		print(f"INFO: TOKENS ON LINES END")

	# Rules:
	# 1. Each " and \ is a separate token
	# 2. Each ocrd-process is a separate token
	# 3. Each -I, -O, and -P is a separate token
	def _ocrd_extract_tokens(self, filepath):
		self.ocrd_lines = []

		# Extract tokens from the ocrd_file
		# Unnecessary empty spaces/lines are discarded
		with open(filepath, mode="r") as ocrd_file:
			for line in ocrd_file:
				curr_line_tokens = []
				line = line.strip().split(' ')
				for token in line:
					if len(token) == 0: continue
					
					# Create separate tokens
					# for quotation marks
					if token.startswith('"'):
						curr_line_tokens.append('"')
						curr_line_tokens.append(token[1:])
					elif token.endswith('"'):
						curr_line_tokens.append(token[:-1])
						curr_line_tokens.append('"')
					else:
						curr_line_tokens.append(token)

				if len(curr_line_tokens) > 0:
					self.ocrd_lines.append(curr_line_tokens)

	# Rules:
	# 1. A single char token must be either: " or \
	# 2. A double char token must be either: -I, -O, or -P
	# 3. Other tokens must contain only VALID_CHARS (constant above)
	def _ocrd_validate_token_symbols(self, lines):
		# Check for invalid symbols/tokens
		for line_index in range (0, len(lines)):
			for token_index in range(0, len(lines[line_index])):
				token = lines[line_index][token_index]
				# Rule 1
				if len(token) == 1:
					if token == '\"' or token == '\\':
						continue
					else:
						print("Syntax error!")
						print(f"Invalid line {line_index+1}, invalid char: {token}!")
						print("Hint: Remove invalid tokens.")
						return False
				# Rule 2
				elif len(token) == 2:
					if token[0] == '-':
						if token[1] == 'I' or \
						token[1] == 'O' or \
						token[1] == 'P':
							continue
						else:
							print("Syntax error!")
							print(f"Invalid line {line_index+1}, invalid token: {token}!")
							print("Hint: Remove invalid tokens.")
							return False
					else:
						if token[0] not in VALID_CHARS or token[1] not in VALID_CHARS:
							print("Syntax error!")
							print(f"Invalid line {line_index+1}, invalid token: {token}!")	
							print("Hint: Remove invalid tokens.")
							return False
				# Rule 3
				else:
					for char in token:
						if char not in VALID_CHARS:
							print("Syntax error!")
							print(f"Invalid line {line_index+1}, invalid token: {token}!")	
							print("Hint: Remove invalid tokens.") 
							print(f"Hint: Tokens cannot contain character: {char}.")
							return False

		return True

	# Rules:
	# 1. The first line starts 
	# with 'ocrd process \'
	# 2. Each line starting from line 2 must have 
	# a single processor call, an input fule, 
	# and an output file. In other words,
	# a minimum amount of tokens.
	# 3. Each ocrd command starts 
	# with a quotation mark ('\"')
	# 4. After a '"' token on each line
	# a valid ocr-d process must follow
	# 5. After a '-I' token on each line
	# only one argument must follow
	# 6. After a '-O' token on each line
	# only one argument must follow
	# 7. After a '-P' token on each line
	# only two arguments must 
	# 8. Only one '-I' and one '-O' token allowed on each line
	# 9. Multiple '-P' tokens are allowed on each line
	# 10. The order of '-I', '-O', and '-P' does not matter
	# Warning:
	# -P are not checked if they are supported 
	# or not by the specific OCR-D processors
	# 11. Each ocrd command ends
	# with a quotation mark ('\"')
	# 12. Each line except the last one ends 
	# with a backslash ('\\').
	# The last line ends with a quotation mark.
	# 13. Invalid chars inside tokens
	# invalidate the token
	def _ocrd_validate_token_syntax(self, lines):
		# Validate the first line syntax (Rule 1)
		expected = ['ocrd', 'process', '\\']
		first_line = lines[0]
		if not first_line == expected:
			print("Syntax error!")
			print(f"Invalid line: {1}!")
			print(f"Expected: '{' '.join(expected)}', tokens: {len(expected)}.")
			print(f"Got: '{' '.join(first_line)}', tokens: {len(first_line)}.")
			print("Hint: Single spaces between the tokens are allowed.")
			return False

		# Validate lines starting from the second line 
		# (Rules 2-12)
		for line_index in range (1, len(lines)):
			# Validate the start of an OCR-D line/command
			# (Rule 3)
			if not lines[line_index][0] == '"':
				print("Syntax error!")
				print(f"Invalid line: {line_index+1}, wrong token at {1}!")
				print(f"Token: {lines[line_index][0]}")
				print("Hint: Commands must start with a \".")
				return False

			# Validate the minimum amount of tokens needed 
			# (Rule 2)
			# This check also prevents index out of 
			# range errors in the following Rule checks
			if len(lines[line_index]) < 8:
				# the last line has one less token than usual
				if line_index == len(lines)-1 and \
					len(lines[-1]) >= 7:
					continue
				print("Syntax error!")
				print(f"Invalid line {line_index+1}, low amount of tokens!")
				print("Hint: Each line must start with a \" and end with a \\.")
				print("Hint: Each line must have a processor call, an input file, and an output file.")
				return False
			
			# Validate the OCR-D processor call in the OCR-D command
			# (Rule 4)
			ocrd_processor = f"ocrd-{lines[line_index][1]}"
			if ocrd_processor not in OCRD_PROCESSORS:
				print("Syntax error!")
				print(f"Ivalid line: {line_index+1}, invalid token: {(lines[line_index][1])}!")
				print("Hint: ocrd-process is spelled incorrectly or does not exists.")
				return False

			# Validate the -I, -O, and -P 
			# (Rules 5-10)
			input_found = False  # track duplicate inputs
			output_found = False  # track duplicate outputs
			processed_tokens = [] # track already matched tokens
			for token_index in range(2, len(lines[line_index])):
				token = lines[line_index][token_index]
				if token == '-I':
					# Duplicate input token found
					if input_found:
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, duplicate -I token at: {token_index}!")
						print("Hint: Only a single input token is allowed!")
						return False
					input_found = True
					# Validate the -I token
					# Exactly one token comes after the -I
					# The token must not be a '"' or '\'
					token_next = lines[line_index][token_index+1]
					if token_next == '\"' or token_next == '\\' or \
						token_next == '-O' or token_next == '-P':
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, wrong or missing input token for: {token_index}")
						return False
					else:
						processed_tokens.append(token_next)
					# print(f"InputToken: {token}, {token_next}")

				elif token == '-O':
					# Duplicate output token found
					if output_found:
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, duplicate -O token at: {token_index}!")
						print("Hint: Only a single output token is allowed!")
						return False
					output_found = True
					# Validate the -O token
					# Exactly one token comes after the -O
					# The token must not be a '"' or '\'
					token_next = lines[line_index][token_index+1]
					if token_next == '\"' or token_next == '\\' or \
						token_next == '-I' or token_next == '-P':
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, wrong or missing output token for: {token_index}")
						return False
					else:
						processed_tokens.append(token_next)
					# print(f"OutputToken: {token}, {token_next}")

				elif token == '-P':
					# Validate the -P token
					# Exactly two tokens comes after the -P
					# The tokens must not be a '"' or '\'
					token_next1 = lines[line_index][token_index+1]
					if token_next1 == '\"' or token_next1 == '\\' or \
						token_next1 == '-I' or token_next1 == '-O':
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, wrong or missing parameter token at: {token_index+1}")
						return False
					else:
						processed_tokens.append(token_next1)

					token_next2 = lines[line_index][token_index+2]
					if token_next2 == '\"' or token_next2 == '\\' or \
						token_next1 == '-I' or token_next1 == '-O':
						print("Syntax Error!")
						print(F"Invalid line: {line_index+1}, wrong or missing parameter token at: {token_index+2}")
						return False
					else:
						processed_tokens.append(token_next2)
					# print(f"ParameterToken: {token}, {token_next1}, {token_next2}")

				else:
					if token == '\"' or token == '\\':
						continue 
					if token in processed_tokens:
						continue
					else:
						print("Syntax Error!")
						print(f"Invalid line: {line_index+1}, wrong unknown token at: {token_index}!")
						print(f"Token: {token}")
						print(f"Hint: Exactly one token must follow -I or -O.")
						print(f"Hint: Exactly two tokens must follow -P.")
						print("Tokens following -I, -O, and -P cannot be a \" or \\.")
						return False

			# Validate the end of an OCR-D command (Rule 11)
			if not lines[line_index][-2] == '"':
				# the last line has no '"' in position -2
				if line_index == len(lines)-1:
					continue
				print("Syntax error!")
				print(f"Invalid line: {line_index+1}!")
				print("Hint: Commands must end with a single \".")
				print("Hint: No whitespaces before the \".")
				return False

			# Validate the end of a OCR-D line (Rule 12)
			if not lines[line_index][-1] == '\\':
				# the last line has no '\\' in position -1
				if line_index == len(lines)-1:
					print(f"Line_index: {line_index}")
					continue
				print("Syntax error!")
				print(f"Invalid line: {line_index+1}!")
				print("Hint: Lines must end with a single \\.")
				return False

		# Validate token symbols (Rule 13)
		if not self._ocrd_validate_token_symbols(lines):
			return False

		return True

	# Rules
	# 1. The input parameter of the second line is the entry-point
	# 2. The input parameter of lines after the second line 
	# are the output parameters of the previous line 
	def _ocrd_validate_io_order(self, lines):
		return False

	# Order:
	# 1. Validate token syntax
	# 2. Validate token order
	# 3. Valudate input/output order
	def _validate_ocrd_file(self, filepath):
		if not exists(filepath):
			print(f"{filepath} does not exist!")
		if not isfile(filepath):
			print(f"{filepath} is not a readable file!")

		print(f"---Converter>_validate_ocrd_file> Validating {filepath}...")

		# Extract tokens from a file
		print(f"---Converter>_validate_ocrd_file> Extracting tokens...")
		self._ocrd_extract_tokens(filepath)

		# Print tokens on the screen
		# self._print_ocrd_tokens()

		# Validate token syntax 
		if self._ocrd_validate_token_syntax(self.ocrd_lines):
			print(f"---Converter>_validate_ocrd_file> Token syntax is valid...")
		else:
			print(f"---Converter>_validate_ocrd_file> Token syntax is invalid!")

		# Validate inputs/outputs order
		if self._ocrd_validate_io_order(self.ocrd_lines):
			print(f"---Converter>_validate_ocrd_file> IO order is valid...")
		else:
			print(f"---Converter>_validate_ocrd_file> IO order is invalid!")

	def _extract_ocrd_commands(self):
		ocrd_commands = []
		for line_index in range(1, len(self.ocrd_lines)):
			first_qm_index = 0
			last_qm_index = 0

			for token_index in range(1, len(self.ocrd_lines[line_index])):
				curr_token = self.ocrd_lines[line_index][token_index]
				if curr_token == '"':
					last_qm_index = token_index
					break

			line = self.ocrd_lines[line_index]
			sub_line = line[first_qm_index+1:last_qm_index]
			ocrd_commands.append(sub_line)

		return ocrd_commands

	def _print_nextflow_tokens(self):
		print(f"INFO: lines in the nextflow file: {len(self.nextflow_lines)}")
		print(f"INFO: TOKENS ON LINES")
		for i in range (0, len(self.nextflow_lines)):
			print(f"nextflow_lines[{i}]: {self.nextflow_lines[i]}")
		print(f"INFO: TOKENS ON LINES END")

	# Rules:
	# 1. Create the default beginning of a Nextflow script
	# 2. For each ocrd command (on each line) a separate 
	# Nextflow process is created
	# 3. Create the main workflow
	def convert_OtoN(self, output_filepath):
		self.nextflow_lines = []

		# Rule 1
		comment_line = "// enables a syntax extension that allows definition of module libraries"
		self.nextflow_lines.append(comment_line.split(' '))
		dsl2 = "nextflow.enable.dsl = 2"
		self.nextflow_lines.append(dsl2.split(' '))
		self.nextflow_lines.append([])

		# The defaul pipeline parameters
		# Set venv_path, workspace_path, and mets_path
		comment_line = "// pipeline parameters"
		self.nextflow_lines.append(comment_line.split(' '))
		venv_path = "\$HOME/venv37-ocrd/bin/activate"
		params_venv = f"params.venv = \"{venv_path}\""
		self.nextflow_lines.append(params_venv.split(' '))
		workspace_path = "$projectDir/ocrd-workspace/"
		params_workspace = f"params.workspace = \"{workspace_path}\""
		self.nextflow_lines.append(params_workspace.split(' '))
		mets_path = "$projectDir/ocrd-workspace/mets.xml"
		params_mets = f"params.mets = \"{mets_path}\""
		self.nextflow_lines.append(params_mets.split(' '))
		self.nextflow_lines.append([])

		ocrd_commands = self._extract_ocrd_commands()


		# Create the nextflow processes
		# Rule 2
		nextflow_processes = []
		for command in ocrd_commands:
			# extract nextflow process name 
			command[0] = f"ocrd-{command[0]}"
			# from the ocrd processor name
			nextflow_process = f"{command[0].replace('-','_')}"
			self.nextflow_lines.append(f"process {nextflow_process}".split(' '))
			self.nextflow_lines.append(['{'])
			self.nextflow_lines.append(['\t','maxForks', '1'])
			self.nextflow_lines.append([])
			self.nextflow_lines.append(['\t','input:'])
			self.nextflow_lines.append(['\t','\t', 'path', 'mets_file'])
			self.nextflow_lines.append([])
			self.nextflow_lines.append(['\t','script:'])
			self.nextflow_lines.append(['\t','"""'])
			self.nextflow_lines.append(['\t','source', '"${params.venv}"'])
			self.nextflow_lines.append(['\t',' '.join(command)])
			self.nextflow_lines.append(['\t', 'deactivate'])
			self.nextflow_lines.append(['\t', '"""'])
			self.nextflow_lines.append(['}'])
			self.nextflow_lines.append([])
			nextflow_processes.append(nextflow_process)


		# Create the main workflow
		# Rule 3
		self.nextflow_lines.append(['workflow'])
		self.nextflow_lines.append(['{'])
		self.nextflow_lines.append(['\t','main:'])
		for process in nextflow_processes:
			self.nextflow_lines.append(['\t','\t', f'{process}(params.mets)'])
		self.nextflow_lines.append(['}'])


		#self._print_nextflow_tokens()
		# Write nextflow line tokens to an output file
		with open(output_filepath, mode="w") as nextflow_file:
			for token_line in self.nextflow_lines:
				string_line = ' '.join(token_line)
				nextflow_file.write(f"{string_line}\n")

def main():
	print("main> Testing the converter")
	converter = Converter()

	print("-------------------------------------------------------------")
	workflow1 = "workflow1.txt"
	nextflow1 = "nextflow1.nf"
	converter._validate_ocrd_file(workflow1)
	print(f"---Converter>convert_OtoN> Converting {workflow1} to {nextflow1}")
	converter.convert_OtoN("nextflow1.nf")

if __name__ == "__main__":
    main()
