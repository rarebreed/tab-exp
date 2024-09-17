from typing import Final
import ipywidgets as iw
from IPython.display import display
import os
Checkbox = iw.Checkbox

Llama3: Final[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
Llama3_1: Final[str] = "meta-llama/Meta-Llama-3.1-8B-Instruct"
FalconMamba: Final[str] = "tiiuae/falcon-mamba-7b"


def model_choice() -> tuple[Checkbox, Checkbox, iw.Dropdown]:
    # Search for directories with "finetuned" in it
    nb_dirs = os.listdir("../notebooks")
    finetuned_dirs = [(d, d) for d in nb_dirs if "finetuned" in d]
    hf_modules = [("llama3:8b", Llama3),
                  ("llama3.1:8b", Llama3_1),
                  ("falcon-mamba:7b", FalconMamba)]
    models = finetuned_dirs + hf_modules
    print(f"{finetuned_dirs=}")

    train = iw.Checkbox(value=False,
                        description="Train model",
                        indent=False)
    new_data = iw.Checkbox(value=False,
                           description="New Data",
                           indent=False)
    model_name = iw.Dropdown(options=models,
                             description="Model Name")
    display(iw.VBox([train, new_data, model_name]))
    return train, new_data, model_name


def get_hf_model(choice: str):
    if "llama3.1" in choice or "Llama-3.1" in choice:
        return Llama3_1
    elif "llama3" in choice or "Llama-3" in choice:
        return Llama3
    elif "falcon" in choice:
        return FalconMamba
    else:
        raise Exception(f"Unknown model for {choice}")


def get_finetuned_name(choice: str):
    model_choice = choice.lower()
    if "llama3.1" in model_choice:
        model = "llama3.1"
    elif "llama3" in model_choice:
        model = "llama3"
    elif "falcon" in model_choice:
        model = "falcon-mamba"
    else:
        raise Exception(f"Unknown model for {choice}")

    nb_dirs = os.listdir("../notebooks")
    version_map: dict[str, str] = {}
    for d in nb_dirs:
        if "finetuned" in d:
            version = int(d.split("-")[-1].replace("v", "")) + 1
            version_map[model] = f"v{version}"
    return f"finetuned-{model}-{version_map[model]}"


def dataset_choice() -> iw.Dropdown:
    dset = iw.Dropdown(options=['train', 'test', 'validate'],
                       value='train',
                       description='Dataset',
                       disabled=False)
    display(dset)
    return dset
