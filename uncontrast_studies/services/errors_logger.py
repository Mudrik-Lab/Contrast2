import pandas
import logging

logger = logging.getLogger("UnConTrast")

# df_studies = pandas.DataFrame.from_records(studies_problematic_data_log)
# df_study_metadata_in_experiment = pandas.DataFrame.from_records(invalid_study_metadata_log)
# df_paradigms = pandas.DataFrame.from_records(invalid_paradigm_data_log)
# df_tasks = pandas.DataFrame.from_records(invalid_task_data_log)
# df_stimuli_presentation_mode = pandas.DataFrame.from_records(invalid_stimuli_presentation_mode_data_log)
# df_missing_value_stimuli = pandas.DataFrame.from_records(invalid_stimuli_metadata_log)
# df_duration_stimuli = pandas.DataFrame.from_records(stimuli_duration_data_log)
# df_modality_stimuli = pandas.DataFrame.from_records(invalid_stimuli_modality_data_log)
# df_missing_category_stimuli = pandas.DataFrame.from_records(stimuli_missing_object_data_log)
# df_incoherent_sample = pandas.DataFrame.from_records(sample_incoherent_data_log)
# df_sample_type = pandas.DataFrame.from_records(sample_type_errors_log)
# df_sample_size = pandas.DataFrame.from_records(sample_size_errors_log)
# df_consciousness_measure = pandas.DataFrame.from_records(invalid_consciousness_measure_data_log)
# df_findings = pandas.DataFrame.from_records(invalid_finding_data_log)
# df_suppression_method = pandas.DataFrame.from_records(invalid_suppression_method_data_log)
# df_processing_domain = pandas.DataFrame.from_records(invalid_processing_domain_data_log)
# df_studies.to_excel(writer, sheet_name="StudyData", index=False)
# df_paradigms.to_excel(writer, sheet_name="ParadigmData", index=False)
# df_incoherent_stimuli.to_excel(writer, sheet_name="IncoherentStimuli", index=False)
# df_missing_value_stimuli.to_excel(writer, sheet_name="MissingValueStimuliData", index=False)
# df_bad_duration_stimuli.to_excel(writer, sheet_name="StimulusDuration", index=False)
# df_missing_category_stimuli.to_excel(writer, sheet_name="StimulusCategory", index=False)
# df_incoherent_sample.to_excel(writer, sheet_name="IncoherentSample", index=False)
# df_sample_type.to_excel(writer, sheet_name="SampleType", index=False)
# df_study_in_experiment.to_excel(writer, sheet_name="ExperimentStudyData", index=False)
# df_consciousness_measure.to_excel(writer, sheet_name="ConsciousnessMeasureData", index=False)


def write_to_log(logs: dict[str, list[str]], file_path):
    log_names = list(logs)
    logs_to_write = []
    for log_name, log_content in logs.items():
        log_index = log_names.index(log_name)
        log_df = {"log_index": log_index, "content": pandas.DataFrame.from_records(log_content), "name": f"{log_name}"}
        if len(log_content) > 0:
            print(f"Writing {log_name} with {len(log_content)} rows to {file_path}")
            logs_to_write.append(log_df)

    try:
        with pandas.ExcelWriter(file_path) as writer:
            for log in logs_to_write:
                data_frame = log["content"]
                name = log["name"].replace("_data_log", "").replace("_errors_log", "")
                data_frame.to_excel(writer, sheet_name=name, index=False)

    except AttributeError as error:
        logger.exception(f"{error.name} occurred while writing to excel")

    return logs_to_write
