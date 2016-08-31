import collections
import json
import logging
import os

from core import rule
from generation.generator import Generator

logging.getLogger().setLevel(logging.DEBUG)


def createSequences(config=None, rules=None, count=None, length=None, number=1):
    """
    Creates new sequences
    :param config: Json configuration file
    :param rules: Path to file with rules
    :param count: Number of events in one sequence
    :param length: Length of one sequence
    :param number: Number of sequences to be created
    :return: A single sequence or a list of sequences.
    """
    if (config is not None):
        if (isinstance(config, str)):
            # noinspection PyUnresolvedReferences
            config = os.path.toAbsolutePath(config)
            with open(config) as f:
                config = json.load(f)

        rules = config["rules"] if "rules" in config else None
        count = int(config["count"]) if "count" in config else None
        length = int(config["length"]) if "length" in config else None
        number = int(config["number"]) if "number" in config else 1

    if (length is None and count is None):
        raise ValueError("Neither sequence length nor event count specified. Please provide at exactly one")
    if (length is not None and count is not None):
        raise ValueError("Sequence length and event count specified. Please provide exactly one")
    if (rules is None):
        raise ValueError("Rules not specified")

    rules = rule.loadFromFile(rules)
    generator = Generator()
    if (length is not None):
        generator.setSeqLength(length)
    if (count is not None):
        generator.setNumberOfEvents(count)
    sequences = generator.setRules(rules).createSequence(number)

    if (isinstance(sequences, collections.Iterable)):
        for seq in sequences:
            seq.rules = rules
    else:
        sequences.rules = rules

    return sequences
