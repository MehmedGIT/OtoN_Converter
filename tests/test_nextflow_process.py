from oton.nextflow_process import Nextflow_Process
from oton.ocrd_validator import OCRD_Validator

def test_line_append():
    """Tests if each NextFlow function appends a number to the processor name
    distinguish processor calls
    """
    input_path = 'tests/assets/workflow_with_duplicate_processors.txt'
    ocrd_validator = OCRD_Validator()
    ocrd_lines = ocrd_validator.extract_and_validate_ocrd_file(input_path)
    ocrd_commands = ocrd_validator.extract_ocrd_commands(ocrd_lines)

    result = []

    for ocrd_command in ocrd_commands:
        index_pos = ocrd_commands.index(ocrd_command)
        nextflow_process = Nextflow_Process(ocrd_command, index_pos, dockerized=False)
        result.append(nextflow_process.process_name)

    expected = [
        "ocrd_olena_binarize_0",
        "ocrd_anybaseocr_crop_1",
        "ocrd_olena_binarize_2",
        "ocrd_cis_ocropy_denoise_3",
        "ocrd_cis_ocropy_deskew_4",
        "ocrd_tesserocr_segment_region_5",
        "ocrd_segment_repair_6",
        "ocrd_cis_ocropy_deskew_7",
        "ocrd_cis_ocropy_clip_8",
        "ocrd_tesserocr_segment_line_9",
        "ocrd_segment_repair_10",
        "ocrd_cis_ocropy_dewarp_11",
        "ocrd_calamari_recognize_12"
    ]

    assert result == expected
