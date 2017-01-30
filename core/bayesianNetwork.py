import igraph
import networkx as nx
from ProbPy import bn
from ProbPy.event import Event
from ProbPy.factor import Factor
from ProbPy.rand_var import RandVar


class Evidence:
    def __init__(self, eventType, occurred):
        self.event = eventType
        self.occurred = occurred

    def __repr__(self):
        return '{}({})'.format(self.event, self.occurred)


# noinspection PyMethodMayBeStatic
class BayesianNetwork:
    def __init__(self, sequence, alpha=0.05):
        self.__alpha = alpha
        self.__sequence = sequence
        self._dcg = None
        self._dag = None
        self.graph = None
        self.filter = []
        self.__randVars = {}
        self.__bn = None

    def createCompleteGraph(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(self.__sequence.eventTypes if len(self.filter) == 0 else self.filter)
        for rule in self.__sequence.calculatedRules:
            if (len(self.filter) == 0 or (rule.trigger in self.filter and rule.response in self.filter)):
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

    def __createTreeFromRules(self, rules):
        tree = {}
        for rule in rules:
            if (len(self.filter) == 0 or (rule.trigger in self.filter and rule.response in self.filter)):
                tree.setdefault(rule.trigger, []).append(rule.response)
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
            if (idx not in obsoleteEdges):
                newEdges.add(edge)

        self._dag = nx.DiGraph()
        self._dag.add_nodes_from(nodes)
        self._dag.add_edges_from(newEdges)
        self.graph = self._dag

        for node in self.graph.nodes():
            self.__randVars[node] = RandVar(node, ['False', 'True'])

        network = []
        for node in self.graph.nodes():
            nodes = [node] + self.graph.predecessors(node)
            n = len(nodes)
            count = 0

            values = []
            while (count < 2 ** n):
                evidence = []
                for i in range(n):
                    evidence.append(Evidence(nodes[i], self.getBit(count, i)))
                count += 1
                values.append(self.__getProb([evidence[0]], evidence[1:]))
            f = Factor([self.__randVars[n] for n in nodes], values)
            network.append((self.__randVars[node], f))
        self.__bn = bn.BayesianNetwork(network)

    def query(self, event, evidence):
        observed = Event()
        for ev in evidence:
            observed.setValue(self.__randVars[ev.event], 'True' if ev.occurred else 'False')
        return self.__bn.eliminationAsk(self.__randVars[event], observed)

    def __getProb(self, variables, conditions):
        if (len(variables) == 1 and len(conditions) == 0):
            v = variables[0]
            p = len(self.__sequence.getEvents(v.event)) / len(self.__sequence.getEvents())
            return p if v.occurred else 1 - p

        if (len(variables) == 1 and len(conditions) == 1):
            v = variables[0]
            c = conditions[0]
            rule = self.__sequence.getCalculatedRule(c.event, v.event)
            if (rule is None or (not v.occurred and not c.occurred)):
                return 1
            if (c.occurred):
                return rule.successResponse if (v.occurred) else 1 - rule.successResponse
            if (v.occurred):
                return rule.successTrigger if (c.occurred) else 1 - rule.successTrigger

        if (len(variables) > 1 and len(conditions) == 0):
            res = 1
            for i in range(len(variables)):
                res *= self.__getProb([variables[i]], variables[i + 1:])
            return res

        if (len(variables) == 1 and len(conditions) > 1):
            v = self.__getProb(variables, [])
            denominator = 1
            res = v
            for i in range(len(conditions)):
                res *= self.__getProb(variables, [conditions[i]]) * self.__getProb([conditions[i]], [])
                denominator *= v
            return res / (v * self.__getProb(conditions, []))

    @staticmethod
    def getBit(byteVal, idx):
        return bool((byteVal & (1 << idx)) != 0)
