import copy

import igraph
import networkx as nx
from networkx.algorithms.dag import topological_sort

NOT_OCCURRED = 0
OCCURRED = 1


class Evidence:
    def __init__(self, eventType, operation):
        self.event = eventType
        self.operation = operation

    def occurred(self):
        return self.operation == OCCURRED

    def __repr__(self):
        return '{}({})'.format(self.event, self.operation)


# noinspection PyMethodMayBeStatic
class BayesianNetwork:
    def __init__(self, sequence, alpha=0.05):
        self.__alpha = alpha
        self.__sequence = sequence
        self._dcg = None
        self._dag = None
        self.graph = None
        self.filter = []

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

    def query(self, event, evidence):
        result = []
        nodes = topological_sort(self.graph)

        e = copy.copy(evidence)
        e.append(Evidence(event, NOT_OCCURRED))
        result.append(self.__enumerateAll(copy.copy(nodes), e))

        e = copy.copy(evidence)
        e.append(Evidence(event, OCCURRED))
        result.append(self.__enumerateAll(copy.copy(nodes), e))
        return self.__normalize(result)

    def __enumerateAll(self, variables, evidence):
        if (len(variables) == 0):
            return 1
        Y = variables.pop()
        parents = self.getParents(Y, evidence)

        if (self.__getEvidence(Y, evidence) is not None):
            return self.__getProb([self.__getEvidence(Y, evidence)], parents) * self.__enumerateAll(variables, evidence)
        else:
            e = copy.copy(evidence)
            x = Evidence(Y, OCCURRED)
            e.append(x)
            val1 = self.__getProb([x], parents) * self.__enumerateAll(variables, e)

            e = copy.copy(evidence)
            x = Evidence(Y, NOT_OCCURRED)
            e.append(e)
            val2 = self.__getProb([x], parents) * self.__enumerateAll(variables, e)
            return val1 + val2

    def getParents(self, node, evidence):
        l = []
        for parent in self.graph.predecessors(node):
            for ev in evidence:
                if (ev.event == parent):
                    l.append(ev)
        return l

    def __getEvidence(self, eventType, evidence):
        for e in evidence:
            if (e.event == eventType):
                return e
        return None

    def __getProb(self, variables, conditions):
        if (len(variables) == 1 and len(conditions) == 0):
            v = variables[0]
            p = len(self.__sequence.getEvents(v.event)) / len(self.__sequence.getEvents())
            return p if v.occurred() else 1 - p

        if (len(variables) == 1 and len(conditions) == 1):
            v = variables[0]
            c = conditions[0]
            rule = self.__sequence.getCalculatedRule(c.event, v.event)
            if (rule is None or (not v.occurred() and not c.occurred())):
                return 1
            if (c.occurred()):
                return rule.successResponse if (v.occurred()) else 1 - rule.successResponse
            if (v.occurred):
                return rule.successTrigger if (c.occurred()) else 1 - rule.successTrigger

        if (len(variables) > 1 and len(conditions) == 0):
            res = 1
            for i in range(len(variables)):
                res *= self.__getProb([variables[i]], variables[i + 1:])
            return res

        if (len(variables) == 1 and len(conditions) > 1):
            v = self.__getProb(variables, [])
            res = v
            for i in range(len(conditions)):
                res *= self.__getProb(variables, [conditions[i]]) * self.__getProb([conditions[i]], [])
                v *= v
            return res / (v * self.__getProb(conditions, []))

    def __normalize(self, result):
        sum = result[0] + result[1]
        return [result[0] / sum, result[1] / sum]
