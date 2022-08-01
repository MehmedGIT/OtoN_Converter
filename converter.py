from os.path import exists, isfile
from string import ascii_letters, digits
import sys
import getopt


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

# Valid characters to be used in the ocrd file
VALID_CHARS = f'-_.{ascii_letters}{digits}'

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
    # ocrd_lines holds the number of lines
    # of the input Ccrd file
    # for each line an inner list is created
    # to hold separate tokens of that line
    self.ocrd_lines = []
    # Convention:
    # nf_lines holds the number of lines
    # of the output Nextflow file
    # for each line an inner list is created
    # to hold separate tokens of that line
    self.nf_lines = []

  def _print_ocrd_tokens(self):
    print(f"INFO: lines in the ocrd file: {len(self.ocrd_lines)}")
    print(f"INFO: TOKENS ON LINES")
    for i in range (0, len(self.ocrd_lines)):
      print(f"ocrd_lines[{i}]: {self.ocrd_lines[i]}")
    print(f"INFO: TOKENS ON LINES END")

  # Rules:
  # 1. Each QM and BACKSLASH is a separate token
  # 2. Each ocrd-process is a separate token
  # 3. Each -I, -O, and -P is a separate token
  def _ocrd_extract_tokens(self, filepath):
    self.ocrd_lines = []

    # Extract tokens from the ocrd_file
    # Unnecessary empty spaces/lines are discarded
    with open(filepath, mode='r') as ocrd_file:
      for line in ocrd_file:
        curr_line_tokens = []
        line = line.strip().split(SPACE)
        for token in line:
          if len(token) == 0: continue
          
          # Create separate tokens
          # for quotation marks
          if token.startswith(QM):
            curr_line_tokens.append(QM)
            curr_line_tokens.append(token[1:])
          elif token.endswith(QM):
            curr_line_tokens.append(token[:-1])
            curr_line_tokens.append(QM)
          else:
            curr_line_tokens.append(token)

        if len(curr_line_tokens) > 0:
          self.ocrd_lines.append(curr_line_tokens)

  # Rules:
  # 1. A single char token must be either: QM or BACKSLASH
  # 2. A double char token must be either: -I, -O, or -P
  # 3. Other tokens must contain only VALID_CHARS
  def _ocrd_validate_token_symbols(self, lines):
    # Check for invalid symbols/tokens
    for line_index in range (0, len(lines)):
      for token_index in range(0, len(lines[line_index])):
        token = lines[line_index][token_index]
        # Rule 1
        if len(token) == 1:
          if token == QM or token == BACKSLASH:
            continue
          else:
            print("Syntax error!")
            print(f"Invalid line {line_index+1}, invalid token: {token}")
            print("Hint: Remove invalid tokens.")
            sys.exit(2)
        # Rule 2
        elif len(token) == 2:
          if token[0] == '-':
            if token[1] == 'I' or \
            token[1] == 'O' or \
            token[1] == 'P':
              continue
            else:
              print("Syntax error!")
              print(f"Invalid line {line_index+1}, invalid token: {token}")
              print("Hint: Remove invalid tokens.")
              sys.exit(2)
          else:
            if token[0] not in VALID_CHARS or token[1] not in VALID_CHARS:
              print("Syntax error!")
              print(f"Invalid line {line_index+1}, invalid token: {token}")  
              print("Hint: Remove invalid tokens.")
              sys.exit(2)
        # Rule 3
        else:
          for char in token:
            if char not in VALID_CHARS:
              print("Syntax error!")
              print(f"Invalid line {line_index+1}, invalid token: {token}")  
              print("Hint: Remove invalid tokens.") 
              print(f"Hint: Tokens cannot contain character: {char}")
              sys.exit(2)

  # Rules:
  # 1. The first line starts with 'ocrd process \'
  # 2. Each line starting from line 2 must have 
  # a single processor call, an input fule, 
  # and an output file. In other words,
  # a minimum amount of tokens.
  # 3. Each ocrd command starts 
  # with a quotation mark (QM)
  # 4. After a QM token on each line
  # a valid ocr-d process must follow
  # 5. After a '-I' token on each line
  # only one argument must follow
  # 6. After a '-O' token on each line
  # only one argument must follow
  # 7. After a '-P' token on each line
  # only two arguments must follow
  # 8. Only one '-I' and one '-O' token allowed on each line
  # 9. Multiple '-P' tokens are allowed on each line
  # 10. The order of '-I', '-O', and '-P' does not matter
  # Warning:
  # -P are not checked if they are supported 
  # or not by the specific OCR-D processors
  # 11. Each ocrd command ends
  # with a quotation mark (QM)
  # 12. Each line except the last one ends 
  # with a backslash (BACKSLASH).
  # The last line ends with a QM.
  # 13. Invalid chars inside tokens
  # invalidate the token
  def _ocrd_validate_token_syntax(self, lines):
    # Validate the first line syntax (Rule 1)
    expected = ['ocrd', 'process', BACKSLASH]
    first_line = lines[0]
    if not first_line == expected:
      print("Syntax error!")
      print(f"Invalid line: {1}!")
      print(f"Expected: '{' '.join(expected)}', tokens: {len(expected)}")
      print(f"Got: '{' '.join(first_line)}', tokens: {len(first_line)}")
      print("Hint: Single spaces between the tokens are allowed.")
      sys.exit(2)

    # Validate lines starting from the second line 
    # (Rules 2-12)
    for line_index in range (1, len(lines)):
      # Validate the start of an OCR-D line/command
      # (Rule 3)
      if not lines[line_index][0] == QM:
        print("Syntax error!")
        print(f"Invalid line: {line_index+1}, wrong token at {1}")
        print(f"Token: {lines[line_index][0]}")
        print(f"Hint: Commands must start with a quotation mark ({QM}).")
        sys.exit(2)

      # Validate the minimum amount of tokens needed 
      # (Rule 2)
      # This check also prevents index out of 
      # range errors in the following Rule checks
      if len(lines[line_index]) < 8:
        # the last line has one less token than usual
        if line_index == len(lines)-1 and len(lines[-1]) >= 7:
          continue
        print("Syntax error!")
        print(f"Invalid line {line_index+1}, low amount of tokens!")
        print(f"Hint: Each line must start with a {QM} and end with a {BACKSLASH}.")
        print("Hint: Each line must have a processor call, an input file, and an output file.")
        sys.exit(2)
      
      # Validate the OCR-D processor call in the OCR-D command
      # (Rule 4)
      ocrd_processor = f"ocrd-{lines[line_index][1]}"
      if ocrd_processor not in OCRD_PROCESSORS:
        print("Syntax error!")
        print(f"Ivalid line: {line_index+1}, invalid token: {lines[line_index][1]}")
        print("Hint: ocrd-process is spelled incorrectly or does not exists.")
        sys.exit(2)

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
            print(F"Invalid line: {line_index+1}, duplicate -I token at: {token_index}")
            print("Hint: Only a single input token is allowed!")
            sys.exit(2)
          input_found = True
          # Validate the -I token
          # Exactly one token comes after the -I
          # The token must not be a QM or a BACKSLASH
          token_next = lines[line_index][token_index+1]
          if token_next == QM or token_next == BACKSLASH or \
            token_next == '-O' or token_next == '-P':
            print("Syntax Error!")
            print(F"Invalid line: {line_index+1}, wrong or missing input token for: {token_index}")
            sys.exit(2)
          else:
            processed_tokens.append(token_next)
          # print(f"InputToken: {token}, {token_next}")

        elif token == '-O':
          # Duplicate output token found
          if output_found:
            print("Syntax Error!")
            print(F"Invalid line: {line_index+1}, duplicate -O token at: {token_index}")
            print("Hint: Only a single output token is allowed!")
            sys.exit(2)
          output_found = True
          # Validate the -O token
          # Exactly one token comes after the -O
          # The token must not be a '"' or '\'
          token_next = lines[line_index][token_index+1]
          if token_next == QM or token_next == BACKSLASH or \
            token_next == '-I' or token_next == '-P':
            print("Syntax Error!")
            print(F"Invalid line: {line_index+1}, wrong or missing output token for: {token_index}")
            sys.exit(2)
          else:
            processed_tokens.append(token_next)
          # print(f"OutputToken: {token}, {token_next}")

        elif token == '-P':
          # Validate the -P token
          # Exactly two tokens comes after the -P
          # The tokens must not be a '"' or '\'
          token_next1 = lines[line_index][token_index+1]
          if token_next1 == QM or token_next1 == BACKSLASH or \
            token_next1 == '-I' or token_next1 == '-O':
            print("Syntax Error!")
            print(F"Invalid line: {line_index+1}, wrong or missing parameter token at: {token_index+1}")
            sys.exit(2)
          else:
            processed_tokens.append(token_next1)

          token_next2 = lines[line_index][token_index+2]
          if token_next2 == QM or token_next2 == BACKSLASH or \
            token_next2 == '-I' or token_next2 == '-O':
            print("Syntax Error!")
            print(F"Invalid line: {line_index+1}, wrong or missing parameter token at: {token_index+2}")
            sys.exit(2)
          else:
            processed_tokens.append(token_next2)
          # print(f"ParameterToken: {token}, {token_next1}, {token_next2}")

        else:
          if token == QM or token == BACKSLASH:
            continue 
          if token in processed_tokens:
            continue
          else:
            print("Syntax Error!")
            print(f"Invalid line: {line_index+1}, wrong unknown token at: {token_index}")
            print(f"Token: {token}")
            print(f"Hint: Exactly one token must follow -I or -O.")
            print(f"Hint: Exactly two tokens must follow -P.")
            print("Tokens following -I, -O, and -P cannot be a quotation mark or a backslash.")
            sys.exit(2)

      # Validate the end of an OCR-D command (Rule 11)
      if not lines[line_index][-2] == QM:
        # the last line has no QM in position -2
        if line_index == len(lines)-1:
          continue
        print("Syntax error!")
        print(f"Invalid line: {line_index+1}")
        print("Hint: Commands must end with a single quotation mark.")
        print("Hint: No whitespaces before the quotation mark.")
        sys.exit(2)

      # Validate the end of a OCR-D line (Rule 12)
      if not lines[line_index][-1] == BACKSLASH:
        # the last line has no '\\' in position -1
        if line_index == len(lines)-1:
          print(f"Line_index: {line_index}")
          continue
        print("Syntax error!")
        print(f"Invalid line: {line_index+1}")
        print("Hint: Lines must end with a single \\.")
        sys.exit(2)

    # Validate token symbols (Rule 13)
    self._ocrd_validate_token_symbols(lines)

  # Rules
  # 1. The input parameter of the second line is the entry-point
  # 2. The input parameter of lines after the second line 
  # are the output parameters of the previous line 
  def _ocrd_validate_io_order(self, lines):
    prev_output = None
    curr_input = None
    curr_output = None

    for line_index in range (1, len(lines)):
      curr_line = lines[line_index]
      curr_input = curr_line[curr_line.index('-I')+1]
      curr_output = curr_line[curr_line.index('-O')+1]

      if prev_output is not None:
        if prev_output != curr_input:
          print(f'Input/Output mismatch error!')
          print(f'{prev_output} on line {line_index} does not match with {curr_input} on line {line_index+1}')
          sys.exit(2)

      prev_output = curr_output

  # Order:
  # 1. Validate token syntax
  # 2. Validate token order
  # 3. Valudate input/output order
  def _validate_ocrd_file(self, filepath):
    if not exists(filepath):
      print(f"OCR-D file {filepath} does not exist!")
      sys.exit(2)
    if not isfile(filepath):
      print(f"OCR-D file {filepath} is not a readable file!")
      sys.exit(2)

    # Extract tokens from a file
    self._ocrd_extract_tokens(filepath)

    # Print tokens on the screen
    # self._print_ocrd_tokens()

    # Validate token syntax 
    self._ocrd_validate_token_syntax(self.ocrd_lines)

    # Validate inputs/outputs order
    self._ocrd_validate_io_order(self.ocrd_lines)

  def _extract_ocrd_commands(self):
    ocrd_commands = []
    for line_index in range(1, len(self.ocrd_lines)):
      first_qm_index = 0
      last_qm_index = 0

      for token_index in range(1, len(self.ocrd_lines[line_index])):
        curr_token = self.ocrd_lines[line_index][token_index]
        if curr_token == QM:
          last_qm_index = token_index
          break

      line = self.ocrd_lines[line_index]
      # Append ocrd- as a prefix
      line[first_qm_index+1] = f'ocrd-{line[first_qm_index+1]}'
      # Extract the ocr-d command without quotation marks
      sub_line = line[first_qm_index+1:last_qm_index]
      ocrd_commands.append(sub_line)

    return ocrd_commands

  def _print_nextflow_tokens(self):
    print(f"INFO: lines in the nextflow file: {len(self.nf_lines)}")
    print(f"INFO: TOKENS ON LINES")
    for i in range (0, len(self.nf_lines)):
      print(f"nf_lines[{i}]: {self.nf_lines[i]}")
    print(f"INFO: TOKENS ON LINES END")

  def _extract_nf_process_name(self, ocrd_processor):
    return f"{ocrd_processor.replace('-','_')}"


  # Rules:  
  # 1. Create the default beginning of a Nextflow script
  # 2. For each ord command (on each line) a separate 
  # Nextflow process is created
  # 3. Create the main workflow
  def convert_OtoN(self, input_path, output_path):
    self._validate_ocrd_file(input_path) 

    # Nextflow script lines
    self.nf_lines = []

    # Rule 1
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

    # Create the nextflow processes
    # Rule 2
    ocrd_commands = self._extract_ocrd_commands()

    # Nextflow processes list
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

    # Create the main workflow
    # Rule 3
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

    # self._print_nextflow_tokens()
    # Write Nextflow line tokens to an output file
    with open(output_path, mode='w') as nextflow_file:
      for token_line in self.nf_lines:
        nextflow_file.write(f'{token_line}\n')

def main(argv):
  input_path = ''
  output_path = ''

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
