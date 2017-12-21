import unittest
import itertools

import networkx as nx
import penaltymodel as pm

import penaltymodel_maxgap as maxgap


class TestInterface(unittest.TestCase):
    """We assume that the generation code works correctly.
    Test that the interface gives a penalty model corresponding to the specification"""
    def test_typical(self):
        graph = nx.complete_graph(3)
        spec = pm.Specification(graph, [0, 1], {(-1, -1): 0, (+1, +1): 0}, pm.SPIN)

        widget = maxgap.get_penalty_model(spec)

        # some quick test to see that the penalty model propogated in
        for v in graph:
            self.assertIn(v, widget.model.linear)
        for (u, v) in graph.edges:
            self.assertIn(u, widget.model.adj[v])

    def test_binary_specification(self):
        graph = nx.Graph()
        for i in range(4):
            for j in range(4, 8):
                graph.add_edge(i, j)

        decision_variables = (0, 1)
        feasible_configurations = ((0, 0), (1, 1))  # equality

        spec = pm.Specification(graph, decision_variables, feasible_configurations, vartype=pm.BINARY)
        widget = maxgap.get_penalty_model(spec)

        self.assertIs(widget.model.vartype, pm.BINARY)

        # test the correctness of the widget
        energies = {}
        for decision_config in itertools.product((0, 1), repeat=2):
            energies[decision_config] = float('inf')

            for aux_config in itertools.product((0, 1), repeat=6):
                sample = dict(enumerate(decision_config + aux_config))
                energy = widget.model.energy(sample)

                energies[decision_config] = min(energies[decision_config], energy)

        for decision_config, energy in energies.items():
            if decision_config in feasible_configurations:
                self.assertAlmostEqual(energy, widget.ground_energy)
            else:
                self.assertGreaterEqual(energy, widget.ground_energy + widget.classical_gap)
