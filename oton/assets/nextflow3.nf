nextflow.enable.dsl = 2

params.workspace_path = "$projectDir/ocrd-workspace/"
params.mets_path = "$projectDir/ocrd-workspace/mets.xml"
params.venv_path = "\$HOME/venv37-ocrd/bin/activate"

process ocrd_dinglehopper_0 {
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
    ocrd-dinglehopper -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_dinglehopper_1 {
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
    ocrd-dinglehopper -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

process ocrd_dinglehopper_2 {
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
    ocrd-dinglehopper -I ${input_dir} -O ${output_dir}
    deactivate
    """
}

workflow {
  main:
    ocrd_dinglehopper_0(params.mets_path, "OCR-D-GT-SEG-BLOCK,OCR-D-OCR", "OCR-D-EVAL-SEG-BLOCK")
    ocrd_dinglehopper_1(ocrd_dinglehopper_0.out, "OCR-D-GT-SEG-LINE,OCR-D-OCR", "OCR-D-EVAL-SEG-LINE")
    ocrd_dinglehopper_2(ocrd_dinglehopper_1.out, "OCR-D-GT-SEG-PAGE,OCR-D-OCR", "OCR-D-EVAL-SEG-PAGE")
}

