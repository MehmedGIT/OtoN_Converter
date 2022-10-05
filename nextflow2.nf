nextflow.enable.dsl = 2

params.workspace = "$projectDir/ocrd-workspace/"
params.mets = "$projectDir/ocrd-workspace/mets.xml"
params.venv = "\$HOME/venv37-ocrd/bin/activate"

process ocrd_cis_ocropy_binarize {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-cis-ocropy-binarize -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_anybaseocr_crop {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-anybaseocr-crop -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_skimage_denoise {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-skimage-denoise -I ${input_dir} -O ${output_dir} -P level-of-operation page
    deactivate
    """
}

process ocrd_tesserocr_deskew {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-tesserocr-deskew -I ${input_dir} -O ${output_dir} -P operation_level page
    deactivate
    """
}

process ocrd_tesserocr_segment {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-tesserocr-segment -I ${input_dir} -O ${output_dir} -P shrink_polygons true
    deactivate
    """
}

process ocrd_cis_ocropy_dewarp {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-cis-ocropy-dewarp -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_tesserocr_recognize {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    source "${params.venv}"
    ocrd-tesserocr-recognize -I ${input_dir} -O ${output_dir} -P textequiv_level glyph -P overwrite_segments true -P model GT4HistOCR_50000000.997_191951
    deactivate
    """
}

workflow {
  main:
    ocrd_cis_ocropy_binarize(params.mets, "OCR-D-IMG", "OCR-D-BIN")
    ocrd_anybaseocr_crop(params.mets, ocrd_cis_ocropy_binarize.out, "OCR-D-CROP")
    ocrd_skimage_denoise(params.mets, ocrd_anybaseocr_crop.out, "OCR-D-BIN-DENOISE")
    ocrd_tesserocr_deskew(params.mets, ocrd_skimage_denoise.out, "OCR-D-BIN-DENOISE-DESKEW")
    ocrd_tesserocr_segment(params.mets, ocrd_tesserocr_deskew.out, "OCR-D-SEG")
    ocrd_cis_ocropy_dewarp(params.mets, ocrd_tesserocr_segment.out, "OCR-D-SEG-DEWARP")
    ocrd_tesserocr_recognize(params.mets, ocrd_cis_ocropy_dewarp.out, "OCR-D-OCR")
}


