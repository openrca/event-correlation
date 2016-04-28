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
    except KeyError:
        raise ValueError("Missing parameter 'rule', 'dist' and/or 'scale'")


def loadEntries(filename):
    logging.info("Loading entries from '{}'".format(filename))
    entries = []

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for line in content:
        logging.debug("Processing line '{}'".format(line))
        try:
            entry = loadEntry(line)
            entries.append(entry)
        except ValueError as ex:
            logging.warning(ex)

    return entries
