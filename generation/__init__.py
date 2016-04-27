import copy
import json
import logging

import core.distribution
import core.rule


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
        return (rule, dist, scale)
    except KeyError as ex:
        raise ValueError("Missing parameter 'rule', 'dist' and/or 'scale'")


def loadEntries(filename):
    logging.info("Loading entries from '{}'".format(filename))
    entries = []

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for i in range(0, len(content)):
        logging.debug("Processing line '{}'".format(content[i]))
        try:
            entry = loadEntry(content[i])
            entries.append(entry)
        except ValueError as ex:
            logging.warning(ex)

    return entries


def printSequence(sequence):
    tokens = []

    seq = copy.copy(sequence.getEvents())
    for i in range(0, sequence.getLength()):
        if (len(seq) > 0 and seq[0].timestamp == i):
            event = seq.pop(0)
            tokens.append(event.getExternalRepresentation())
        else:
            tokens.append("_")
    return "".join(tokens)
