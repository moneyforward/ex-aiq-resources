import yaml
import os


def load_prompt_from_yaml(filepath, field_name):
    """
    Loads a prompt from a YAML file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' was not found.")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            if data is None:
                raise ValueError(f"The file '{filepath}' is empty or not valid YAML.")
            prompt_text = data.get(field_name)

            if prompt_text is None:
                raise KeyError(f"No '{field_name}' key found in the YAML file.")

            return prompt_text
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}") from e
