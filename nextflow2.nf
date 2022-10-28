nextflow.enable.dsl = 2

params.workspace_path = "$projectDir/ocrd-workspace/"
params.mets_path = "$projectDir/ocrd-workspace/mets.xml"
params.venv_path = "\$HOME/venv37-ocrd/bin/activate"

process ocrd_cis_ocropy_binarize_0 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-cis-ocropy-binarize -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_anybaseocr_crop_1 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-anybaseocr-crop -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_skimage_denoise_2 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-skimage-denoise -I ${input_dir} -O ${output_dir} -P level-of-operation page
    deactivate
    """
}

process ocrd_tesserocr_deskew_3 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-tesserocr-deskew -I ${input_dir} -O ${output_dir} -P operation_level page
    deactivate
    """
}

process ocrd_tesserocr_segment_4 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-tesserocr-segment -I ${input_dir} -O ${output_dir} -P shrink_polygons true
    deactivate
    """
}

process ocrd_cis_ocropy_dewarp_5 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-cis-ocropy-dewarp -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_tesserocr_recognize_6 {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    path mets_file

  script:
    """
    source "${params.venv_path}"
    ocrd-tesserocr-recognize -I ${input_dir} -O ${output_dir} -P textequiv_level glyph -P overwrite_segments true -P model GT4HistOCR_50000000.997_191951
    deactivate
    """
}

workflow {
  main:
    ocrd_cis_ocropy_binarize_0(params.mets_path, "OCR-D-IMG", "OCR-D-BIN")
    ocrd_anybaseocr_crop_1(ocrd_cis_ocropy_binarize_0.out, "OCR-D-BIN", "OCR-D-CROP")
    ocrd_skimage_denoise_2(ocrd_anybaseocr_crop_1.out, "OCR-D-CROP", "OCR-D-BIN-DENOISE")
    ocrd_tesserocr_deskew_3(ocrd_skimage_denoise_2.out, "OCR-D-BIN-DENOISE", "OCR-D-BIN-DENOISE-DESKEW")
    ocrd_tesserocr_segment_4(ocrd_tesserocr_deskew_3.out, "OCR-D-BIN-DENOISE-DESKEW", "OCR-D-SEG")
    ocrd_cis_ocropy_dewarp_5(ocrd_tesserocr_segment_4.out, "OCR-D-SEG", "OCR-D-SEG-DEWARP")
    ocrd_tesserocr_recognize_6(ocrd_cis_ocropy_dewarp_5.out, "OCR-D-SEG-DEWARP", "OCR-D-OCR")
}


