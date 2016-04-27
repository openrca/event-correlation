import copy
import json
import logging

import core.distribution
import core.event


class Rule:
    def __init__(self, trigger, response, distribution, confidence=1):
        """ Represents a single rule

        Parameters:
            trigger: An event that causes this rule to trigger
            response: An event that follows after the tirgger
            distribution: The distribution used to calculate the time lag between trigger and response
            confidence: Probability that the response really follows the trigger
        """

        # TODO probability that response arises without trigger is missing

        self.trigger = trigger
        self.response = response
        self.distribution = distribution
        self.confidence = confidence

    def getResponseTimestamp(self):
        return self.distribution.getPDFValue()

    def getResponse(self):
        return copy.copy(self.response)

    def getTrigger(self):
        return copy.copy(self.trigger)

    def getConfidence(self):
        return self.confidence

    @staticmethod
    def load(value):
        tokens = value.split(";")

        if (len(tokens) != 4):
            raise ValueError("Unknown format '{}'".format(value))

    @staticmethod
    def loadRules(name):
        """ Loads a set of rules from a file
        The file has to store one role per line with the following format

            <TRIGGER>; <RESPONSE>; <DISTRIBUTION>; <CONFIDENCE>
        """
        logging.info("Loading rules from '{}'".format(name))
        rules = []

        with open(name, "r") as file:
            for line in file:
                try:
                    logging.debug("Processing line '{}'".format(line))
                    rule = Rule.load(line)
                    rules.append(rule)
                except ValueError as ex:
                    logging.warning(ex)
        return rules


def load(value):
    """ Load a rule from a json string
    Parameter:
        trigger, response, dist, confidence
    Throws:
        ValueException
    """

    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        trigger = core.event.load(value["trigger"])
        response = core.event.load(value["response"])
        confidence = float(value["confidence"])
        dist = core.distribution.load(value["dist"])

        return Rule(trigger, response, dist, confidence)
    except KeyError as ex:
        raise ValueError("Missing parameter 'trigger', 'response', 'confidence' and/or 'dist'")


def loadFromFile(filename):
    logging.info("Loading rules from '{}'".format(filename))
    rules = []

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for i in range(0, len(content)):
        logging.debug("Processing line '{}'".format(content[i]))
        try:
            entry = load(content[i])
            rules.append(entry)
        except ValueError as ex:
            logging.warning(ex)

    return rules
