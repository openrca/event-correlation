import json
import logging

import core.distribution
import core.event


class Rule:
    def __init__(self, trigger, response, distribution, triggerConfidence=1.0, responseConfidence=1.0):
        """ Represents a single rule

        Parameters:
            trigger: An event type that causes this rule to trigger
            response: An event type that follows after the trigger
            distribution: The distribution used to calculate the time lag between trigger and response
            triggerConfidence: Probability that the trigger is really triggered
            responseConfidence: Probability that the response really follows the trigger
        """
        if (isinstance(trigger, core.event.Event)):
            self.trigger = trigger.getEventType()
        else:
            self.trigger = trigger
        if (isinstance(response, core.event.Event)):
            self.response = response.getEventType()
        else:
            self.response = response
        self.distribution = distribution
        self.triggerConfidence = triggerConfidence
        self.responseConfidence = responseConfidence

    def getResponseTimestamp(self):
        return self.distribution.getRandom()

    def getResponse(self):
        return self.response

    def getTrigger(self):
        return self.trigger

    def getResponseConfidence(self):
        return self.responseConfidence

    def getTriggerConfidence(self):
        return self.triggerConfidence

    def getDistribution(self):
        return self.distribution

    def asJson(self):
        return {
            "trigger": self.trigger,
            "response": self.response,
            "dist": self.distribution.asJson(),
            "triggerConfidence": self.triggerConfidence,
            "responseConfidence": self.responseConfidence
        }

    def __eq__(self, other):
        if (not isinstance(other, Rule)):
            return False
        return self.trigger == other.trigger and self.response == other.response \
               and self.distribution == other.distribution and self.triggerConfidence == other.triggerConfidence \
               and self.responseConfidence == other.responseConfidence

    def __hash__(self):
        return hash(self.trigger) + hash(self.response) + hash(self.distribution) + hash(self.triggerConfidence) \
               + hash(self.responseConfidence)


def load(value):
    """ Load a rule from a json string
    Parameter:
        trigger, response, dist, triggerConfidence, responseConfidence
    Throws:
        ValueException
    """

    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        trigger = value["trigger"]
        response = value["response"]
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
