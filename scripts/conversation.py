import hydra
from hydra.utils import instantiate

from dementia_agent.agent import DementiaAgent
from dementia_agent.knowledge_graph.visualize import visualize_graph


@hydra.main(config_path="../configs", config_name="config.yaml", version_base='1.2')
def conversation(cfg):
    agent: DementiaAgent = instantiate(cfg.agent, _convert_='object')
    visualize_graph(agent.graph_interface.knowledge_graph)
    agent.chat()

if __name__ == "__main__":
    conversation()