from pkg_resources import resource_filename
from oton.converter import Converter
from re import sub
import os


def clean_up(path):
    """Cleans up test artifacts from file system
    """
    if os.path.isfile(path):
        os.remove(path)


def test_conversion_wo_docker():
    """E2E test for an OCR-D workflow conversion using native ocrd_all
    """

    input_path = resource_filename(__name__, 'assets/workflow.txt')
    output_path = resource_filename(__name__, 'assets/output_workflow.nf')

    Converter().convert_OtoN(input_path=input_path, output_path=output_path, dockerized=True)

    expected_workflow = """workflow {
            main:
                ocrd_cis_ocropy_binarize_0(params.mets_path, "OCR-D-IMG", "OCR-D-BIN")
                ocrd_anybaseocr_crop_1(ocrd_cis_ocropy_binarize_0.out, "OCR-D-BIN", "OCR-D-CROP")
                ocrd_skimage_binarize_2(ocrd_anybaseocr_crop_1.out, "OCR-D-CROP", "OCR-D-BIN2")
                ocrd_skimage_denoise_3(ocrd_skimage_binarize_2.out, "OCR-D-BIN2", "OCR-D-BIN-DENOISE")
                ocrd_tesserocr_deskew_4(ocrd_skimage_denoise_3.out, "OCR-D-BIN-DENOISE", "OCR-D-BIN-DENOISE-DESKEW")
                ocrd_cis_ocropy_segment_5(ocrd_tesserocr_deskew_4.out, "OCR-D-BIN-DENOISE-DESKEW", "OCR-D-SEG")
                ocrd_cis_ocropy_dewarp_6(ocrd_cis_ocropy_segment_5.out, "OCR-D-SEG", "OCR-D-SEG-LINE-RESEG-DEWARP")
                ocrd_calamari_recognize_7(ocrd_cis_ocropy_dewarp_6.out, "OCR-D-SEG-LINE-RESEG-DEWARP", "OCR-D-OCR")
        }"""
    expected_normalized = sub(r'\s+', '', expected_workflow)

    with open(output_path, mode='r', encoding='utf-8') as fp:
        wf = fp.read()
        no_tab_string = sub(r'\t+', '', wf)
        no_spaces_result = sub(r'\s+', '', no_tab_string)

    clean_up(output_path)

    assert expected_normalized in no_spaces_result


def test_conversion_with_docker():
    """E2E test for an OCR-D workflow conversion using the Docker flag.
    We test for success by looking for a exemplary line that is executed by Docker.
    """

    input_path = resource_filename(__name__, 'assets/workflow.txt')
    output_path = resource_filename(__name__, 'assets/output_docker_workflow.nf')

    Converter().convert_OtoN(input_path=input_path, output_path=output_path, dockerized=True)
    expected = """${params.docker_command} ocrd-cis-ocropy-binarize -I ${input_dir} -O ${output_dir}"""

    with open(output_path, mode='r', encoding='utf-8') as fp:
        wf = fp.read()

    clean_up(output_path)

    assert expected in wf


def test_models_volume_for_docker():
    """E2E test for a Docker-base OCR-D workflow conversion with a models directory.
    We test if the resulting NextFlow script has a volume for mounting the text detection models."""

    input_path = resource_filename(__name__, 'assets/workflow.txt')
    output_path = resource_filename(__name__, 'assets/output_docker_workflow.nf')

    Converter().convert_OtoN(input_path=input_path, output_path=output_path, dockerized=True)
    expected = "docker run --rm -u \\$(id -u) -v $params.docker_volume -v $params.docker_models -w $params.docker_pwd -- $params.docker_image"

    with open(output_path, mode='r', encoding='utf-8') as fp:
        wf = fp.read()

    clean_up(output_path)

    assert expected in wf
