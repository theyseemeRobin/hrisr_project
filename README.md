# [PROJECT NAME HERE]
This repo contains the code for an LLM agent that is designed to interact with people suffering from dementia. 
This project was part of the course ["Human Robot Interaction for Social Robots"](https://ocasys.rug.nl/current/catalog/course/WMAI027-05)
at the University of Groningen. 

## Installation
First, [install ollama](https://ollama.com/download), and pull the embedding model specified in
[retriever.yaml](configs/agent/retriever/retriever.yaml). By default, it is all-minilm:
```bash
ollama pull all-minilm
```

Then install the package
```bash
pip install .
```

## Usage
First place you Gemini API token in the [.env](.env) file. Then run the script:
```bash
# run the agent
python -m scripts.conversation
```
