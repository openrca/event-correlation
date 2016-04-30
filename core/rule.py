import copy
import json
import logging

import core.distribution
import core.event


class Rule:
    def __init__(self, trigger, response, distribution, triggerConfidence=1.0, responseConfidence=1.0):
        """ Represents a single rule

        Parameters:
            trigger: An event that causes this rule to trigger
            response: An event that follows after the tirgger
            distribution: The distribution used to calculate the time lag between trigger and response
            triggerConfidence: Probability that the trigger is really triggered
            responseConfidence: Probability that the response really follows the trigger
        """

        # TODO probability that response arises without trigger is missing

        self.trigger = trigger
        self.response = response
        self.distribution = distribution
        self.triggerConfidence = triggerConfidence
        self.responseConfidence = responseConfidence

    def getResponseTimestamp(self):
        return self.distribution.getPDFValue()

    def getResponse(self):
        return copy.copy(self.response)

    def getTrigger(self):
        return copy.copy(self.trigger)

    def getResponseConfidence(self):
        return self.responseConfidence

    def getTriggerConfidence(self):
        return self.triggerConfidence

    def asJson(self):
        return {
            "trigger": self.trigger.asJson(),
            "response": self.trigger.asJson(),
            "dist": self.distribution.asJson(),
            "triggerConfidence": self.triggerConfidence,
            "responseConfidence": self.responseConfidence
        }


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
        triggerConfidence = float(value["triggerConfidence"])
        responseConfidence = float(value["responseConfidence"])
        dist = core.distribution.load(value["dist"])

        return Rule(trigger, response, dist, triggerConfidence, responseConfidence)
    except KeyError:
        raise ValueError("Missing parameter 'trigger', 'response', 'triggerConfidence',"
                         " 'responseConfidence' and/or 'dist'")


def loadFromFile(filename):
    logging.info("Loading rules from '{}'".format(filename))
    rules = []

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for item in content:
        logging.debug("Processing line '{}'".format(item))
        try:
            entry = load(item)
            rules.append(entry)
        except ValueError as ex:
            logging.warning(ex)

    return rules
