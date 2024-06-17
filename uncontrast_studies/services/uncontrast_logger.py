import pandas
import logging

logger = logging.getLogger(__name__)


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
