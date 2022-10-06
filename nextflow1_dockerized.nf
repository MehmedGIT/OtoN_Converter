nextflow.enable.dsl = 2

params.workspace_path = "$projectDir/ocrd-workspace/"
params.mets_path = "$projectDir/ocrd-workspace/mets.xml"
params.docker_pwd = "/ocrd-workspace"
params.docker_volume = "$params.workspace_path:$params.docker_pwd"
params.docker_image = "ocrd/all:maximum"
params.docker_command = "docker run --rm -u \$(id -u) -v $params.docker_volume -w $params.docker_pwd -- $params.docker_image"

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
    ${params.docker_command} ocrd-cis-ocropy-binarize -I ${input_dir} -O ${output_dir}
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
    ${params.docker_command} ocrd-anybaseocr-crop -I ${input_dir} -O ${output_dir}
    """
}

process ocrd_skimage_binarize {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    ${params.docker_command} ocrd-skimage-binarize -I ${input_dir} -O ${output_dir} -P method li
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
    ${params.docker_command} ocrd-skimage-denoise -I ${input_dir} -O ${output_dir} -P level-of-operation page
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
    ${params.docker_command} ocrd-tesserocr-deskew -I ${input_dir} -O ${output_dir} -P operation_level page
    """
}

process ocrd_cis_ocropy_segment {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    ${params.docker_command} ocrd-cis-ocropy-segment -I ${input_dir} -O ${output_dir} -P level-of-operation page
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
    ${params.docker_command} ocrd-cis-ocropy-dewarp -I ${input_dir} -O ${output_dir}
    """
}

process ocrd_calamari_recognize {
  maxForks 1

  input:
    path mets_file
    val input_dir
    val output_dir

  output:
    val output_dir

  script:
    """
    ${params.docker_command} ocrd-calamari-recognize -I ${input_dir} -O ${output_dir} -P checkpoint_dir qurator-gt4histocr-1.0
    """
}

workflow {
  main:
    ocrd_cis_ocropy_binarize(params.mets_path, "OCR-D-IMG", "OCR-D-BIN")
    ocrd_anybaseocr_crop(params.mets_path, ocrd_cis_ocropy_binarize.out, "OCR-D-CROP")
    ocrd_skimage_binarize(params.mets_path, ocrd_anybaseocr_crop.out, "OCR-D-BIN2")
    ocrd_skimage_denoise(params.mets_path, ocrd_skimage_binarize.out, "OCR-D-BIN-DENOISE")
    ocrd_tesserocr_deskew(params.mets_path, ocrd_skimage_denoise.out, "OCR-D-BIN-DENOISE-DESKEW")
    ocrd_cis_ocropy_segment(params.mets_path, ocrd_tesserocr_deskew.out, "OCR-D-SEG")
    ocrd_cis_ocropy_dewarp(params.mets_path, ocrd_cis_ocropy_segment.out, "OCR-D-SEG-LINE-RESEG-DEWARP")
    ocrd_calamari_recognize(params.mets_path, ocrd_cis_ocropy_dewarp.out, "OCR-D-OCR")
}


