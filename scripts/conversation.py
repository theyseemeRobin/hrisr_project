import hydra
from hydra.utils import instantiate

from dementia_agent.knowledge_graph.visualize import visualize_graph


@hydra.main(config_path="../configs", config_name="config.yaml", version_base='1.2')
def conversation(cfg):
    kg = instantiate(cfg.knowledge_graph, _convert_="object")
    visualize_graph(kg)
    gemini = instantiate(cfg.gemini, _convert_="object")
    gemini.start_conversation()

if __name__ == "__main__":
    conversation()