import igraph
import networkx as nx


class BayesianNetwork:
    def __init__(self, sequence, alpha=0.05):
        self.__alpha = alpha
        self.__sequence = sequence
        self._dcg = None
        self._dag = None
        self.graph = None

    def createCompleteGraph(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(self.__sequence.eventTypes)
        for rule in self.__sequence.calculatedRules:
            graph.add_edge(rule.trigger, rule.response)
        self._dcg = graph
        self.graph = self._dcg

    def createGraph(self, root):
        tree = self.__createTreeFromRules(self.__sequence.calculatedRules)
        edges = set()
        processed = set()

        graph = nx.DiGraph()
        if (root is None):
            return graph
        elements = [root]
        while len(elements) > 0:
            newElements = []
            for element in elements:
                if (element in processed):
                    continue
                processed.add(element)

                for event in tree[element]:
                    graph.add_node(event)
                    if (self.__sequence.getCalculatedRule(element, event) is not None):
                        edges.add((element, event))
                    newElements.append(event)
            elements = set(newElements)

        graph.add_edges_from(edges)
        self._dcg = graph
        self.graph = self._dcg

    @staticmethod
    def __createTreeFromRules(rules):
        tree = {}
        for rule in rules:
            tree.setdefault(rule.trigger, []).append(rule.response)
        for rule in rules:
            tree.setdefault(rule.response, []).append(rule.trigger)
        return tree

    def learnStructure(self):
        edges = self._dcg.edges()
        nodes = self._dcg.nodes()

        graph = igraph.Graph(directed=True)
        for node in nodes:
            graph.add_vertex(node)

        for trigger, response in edges:
            graph.add_edge(trigger, response)

        newEdges = set()
        obsoleteEdges = graph.feedback_arc_set()
        for idx, edge in enumerate(edges):
            if(idx not in obsoleteEdges):
                newEdges.add(edge)

        self._dag = nx.DiGraph()
        self._dag.add_nodes_from(nodes)
        self._dag.add_edges_from(newEdges)
        self.graph = self._dag
