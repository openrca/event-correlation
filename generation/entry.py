import json
import logging

import core
from core.distribution import ExponentialDistribution
from core.rule import Rule


class Entry:
    def __init__(self, rule: Rule, dist=ExponentialDistribution(), scale=1.0):
        self.rule = rule
        self.lastTime = 0
        self.dist = dist
        self.scale = scale

    def getOccurrenceProb(self, t):
        return self.dist.getCDFValue(t - self.lastTime) * self.scale

    def __eq__(self, other):
        if (not isinstance(other, Entry)):
            return False
        return self.rule == other.rule and self.dist == other.dist and self.scale == other.scale

    def __hash__(self):
        return hash(self.rule) + hash(self.dist) + hash(self.scale)

    def __repr__(self):
        return str(self.rule) + " | " + str(self.dist)


def loadEntry(value):
    """ Loads a entry from a json string
    Parameter:
        rule, dist, scale
    Throws:
        ValueException
    """

    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        rule = core.rule.load(value["rule"])
        dist = core.distribution.load(value["dist"])
        scale = float(value["scale"])
        return Entry(rule, dist, scale)
    except KeyError:
        raise ValueError("Missing parameter 'rule', 'dist' and/or 'scale'")


def loadEntries(filename):
    logging.info("Loading entries from '{}'".format(filename))
    entries = []

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for line in content:
        logging.debug("Processing line '{}'".format(line))
        entry = loadEntry(line)
        entries.append(entry)

    return entries
