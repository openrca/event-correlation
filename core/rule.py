import json
import logging

import core.distribution
import core.event


class Rule:
    def __init__(self, trigger, response, distribution, successTrigger=1.0, successResponse=1.0):
        """ Represents a single rule

        Parameters:
            trigger: An event type that causes this rule to trigger
            response: An event type that follows after the trigger
            distribution: The distribution used to calculate the time lag between trigger and response
            successTrigger: Probability that the trigger is really triggered
            successResponse: Probability that the response really follows the trigger
        """
        if (isinstance(trigger, core.event.Event)):
            self.trigger = trigger.eventType
        else:
            self.trigger = trigger
        if (isinstance(response, core.event.Event)):
            self.response = response.eventType
        else:
            self.response = response
        self.distribution = distribution
        self.successTrigger = successTrigger
        self.successResponse = successResponse
        self.likelihood = -1

    def getResponseTimestamp(self):
        return self.distribution.getRandom()

    def asJson(self):
        return {
            "trigger": self.trigger,
            "response": self.response,
            "dist": self.distribution.asJson(),
            "successTrigger": self.successTrigger,
            "successResponse": self.successResponse,
            "likelihood": self.likelihood
        }

    def __eq__(self, other):
        if (not isinstance(other, Rule)):
            return False
        return self.trigger == other.trigger and self.response == other.response \
               and self.distribution == other.distribution and self.successTrigger == other.successTrigger \
               and self.successResponse == other.successResponse

    def __hash__(self):
        return hash(self.trigger) + hash(self.response) + hash(self.distribution) + hash(self.successTrigger) \
               + hash(self.successResponse)

    def __str__(self):
        response = str(self.trigger) + " -> "
        if (self.response is not None):
            response += str(self.response) + " (" + str(self.distribution) + ")"
        else:
            response += "_"
        return response


def load(value):
    """ Load a rule from a json string
    Parameter:
        trigger, response, dist, successTrigger, successResponse
    Throws:
        ValueException
    """

    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        trigger = value["trigger"]
        successTrigger = float(value["successTrigger"])

        if ("response" in value):
            try:
                response = value["response"]
                successResponse = float(value["successResponse"])
                dist = core.distribution.load(value["dist"])
            except KeyError:
                raise ValueError("Missing parameter 'successResponse' and/or 'dist'")
        else:
            response = None
            dist = None
            successResponse = None

        rule = Rule(trigger, response, dist, successTrigger, successResponse)
        if ("likelihood" in value):
            rule.likelihood = float(value["likelihood"])
        return rule
    except KeyError:
        raise ValueError("Missing parameter 'trigger' and/or 'successTrigger'")


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
