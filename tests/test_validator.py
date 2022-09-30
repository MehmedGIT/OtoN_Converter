from oton.ocrd_validator import OCRD_Validator

def get_expected_output():
    """Returns the expected validation outputs for tests/assets/workflow.txt and
    tests/assets/workflow_docker.txt.
    """
    return [
        ['ocrd', 'process', '\\'],
        ['"', 'cis-ocropy-binarize', '-I', 'OCR-D-IMG', '-O', 'OCR-D-BIN', '"', '\\'],
        ['"', 'anybaseocr-crop', '-I', 'OCR-D-BIN', '-O', 'OCR-D-CROP', '"', '\\'],
        ['"', 'skimage-binarize', '-I', 'OCR-D-CROP', '-O', 'OCR-D-BIN2', '-P', 'method', 'li', '"', '\\'],
        ['"', 'skimage-denoise', '-I', 'OCR-D-BIN2', '-O', 'OCR-D-BIN-DENOISE', '-P', 'level-of-operation', 'page', '"', '\\'],
        ['"', 'tesserocr-deskew', '-I', 'OCR-D-BIN-DENOISE', '-O', 'OCR-D-BIN-DENOISE-DESKEW', '-P', 'operation_level', 'page', '"', '\\'],
        ['"', 'cis-ocropy-segment', '-I', 'OCR-D-BIN-DENOISE-DESKEW', '-O', 'OCR-D-SEG', '-P', 'level-of-operation', 'page', '"', '\\'],
        ['"', 'cis-ocropy-dewarp', '-I', 'OCR-D-SEG', '-O', 'OCR-D-SEG-LINE-RESEG-DEWARP', '"', '\\'],
        ['"', 'calamari-recognize', '-I', 'OCR-D-SEG-LINE-RESEG-DEWARP', '-O', 'OCR-D-OCR', '-P', 'checkpoint_dir', 'qurator-gt4histocr-1.0', '"']
    ]

def test_workflow_without_docker():
    """E2E test for an OCR-D workflow using native ocrd_all
    """
    input_path = 'tests/assets/workflow.txt'
    result = OCRD_Validator().validate_ocrd_file(input_path)

    assert result == get_expected_output()
