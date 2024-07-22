# tab-exp

This is an experiment to convert tabular or structured data into textual information that can be used by a transformer.
Generally, transformers do not work well on tabular data, and only do about as well as Gradient Boosted Decision Trees.
Transformers in particular work best on unstructured data like text, images or audio.

The idea here is to convert tabular data into textual information that can be used by a transformer by converting each
row of data into a document. These new documents will be created through synthetic data for fine tuning the llama3 LLM.

## How to use

Currently, this is only setup for linux and windows (it should work on a mac, but may not have GPU acceleration, so it
was not included as a pixi platform).

First, install pixi

```bash
# For windows
winget install prefix-dev.pixi
```

```bash
# For linux
curl -fsSL https://pixi.sh/install.sh | bash

# Install python build dependencies
# for ubuntu
sudo apt install -y build-essential python3-pip python3-venv python3-dev
```

Then cd into the tab-exp directory and run:

```bash
pixi install
```

## Generate Synthetic Data

TODO: Describe how to generate synthetic data using the tab_exp.tab module.

Still need to test out the module more.

## Fine tuning

TODO: Describe how to fine tune the llama3 model using the synthetic data. That is created.

We need the tokenizer for llama3 to create the inputs from the new custom dataset for fine tuning.