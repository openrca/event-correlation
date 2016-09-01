import json
import logging
import os

import core.distribution
from core.event import Event


class Rule:
    def __init__(self, trigger, response, distributionResponse, distributionTrigger=None, successTrigger=1.0,
                 successResponse=1.0, data=None):
        """ Represents a single rule

        Parameters:
            trigger: An event type that causes this rule to trigger
            response: An event type that follows after the trigger
            distributionResponse: The distribution used to calculate the time lag between trigger and response
            distributionTrigger: The inter-arrival distribution of the trigger event
            successTrigger: Probability that the trigger is really triggered
            successResponse: Probability that the response really follows the trigger
            data: Optional parameter to store additional information from rule matching.
        """
        if data is None:
            data = {}
        if (isinstance(trigger, Event)):
            self.trigger = trigger.eventType
        else:
            self.trigger = trigger
        if (isinstance(response, Event)):
            self.response = response.eventType
        else:
            self.response = response
        self.distributionTrigger = distributionTrigger
        self.distributionResponse = distributionResponse
        self.successTrigger = successTrigger
        self.successResponse = successResponse
        self.likelihood = -1
        self.data = data

    def getResponseTimestamp(self):
        return self.distributionResponse.getRandom()

    def matches(self, trigger, response):
        """ Checks if this rule has the given trigger and response. """
        if (isinstance(trigger, Event)):
            trigger = trigger.eventType
        if (isinstance(response, Event)):
            response = response.eventType

        return trigger == self.trigger and response == self.response

    def asJson(self):
        d = {"likelihood": self.likelihood, "data": self.data, "trigger": {
            "event": self.trigger,
            "dist": self.distributionTrigger if self.distributionTrigger is not None else "",
            "success": self.successTrigger
        }}
        if (self.response is not None):
            d["response"] = {"event": self.response, "success": self.successResponse,
                             "dist": self.distributionResponse if self.distributionResponse is not None else ""}
        return d

    def __eq__(self, other):
        if (not isinstance(other, Rule)):
            return False
        return self.trigger == other.trigger and self.response == other.response \
               and self.distributionResponse == other.distributionResponse \
               and self.distributionTrigger == other.distributionTrigger \
               and self.successTrigger == other.successTrigger and self.successResponse == other.successResponse \
               and self.likelihood == other.likelihood

    def __hash__(self):
        return hash(self.trigger) + hash(self.response) + hash(self.distributionTrigger) \
               + hash(self.distributionResponse) + hash(self.successTrigger) + hash(self.successResponse) \
               + hash(self.likelihood)

    def __str__(self):
        response = str(self.trigger)
        if (self.distributionTrigger is not None):
            response += " ({})".format(self.distributionTrigger)
        response += " -> "
        if (self.response is not None):
            response += str(self.response)
            if (self.distributionResponse is not None):
                response += " ({})".format(self.distributionResponse)
        else:
            response += "_"
        return response


def load(value):
    """ Load a rule from a json string
    Parameter:
        trigger, response
    Throws:
        ValueException
    """

    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        trigger = value["trigger"]
        eventTrigger = trigger["event"]
        successTrigger = float(trigger["success"])
        distTrigger = core.distribution.load(trigger["dist"])

        if ("response" in value):
            try:
                response = value["response"]
                eventResponse = response["event"]
                successResponse = float(response["success"])
                distResponse = core.distribution.load(response["dist"])
            except KeyError:
                raise ValueError("Missing parameter 'event' and/or 'success' and/or 'dist' in 'response'.")
        else:
            eventResponse = None
            successResponse = None
            distResponse = None

        rule = Rule(eventTrigger, eventResponse, distResponse, distTrigger, successTrigger, successResponse)
        if ("likelihood" in value):
            rule.likelihood = float(value["likelihood"])
        if ("data" in value):
            rule.data = value["data"]
        return rule
    except KeyError:
        raise ValueError("Missing parameter 'trigger' with 'event' and/or 'success' and/or 'dist'.")


def loadFromFile(filename):
    logging.info("Loading rules from '{}'".format(filename))
    rules = []
    # noinspection PyUnresolvedReferences
    filename = os.path.toAbsolutePath(filename)

    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for item in content:
        logging.debug("Processing line '{}'".format(item))
        try:
            rules.append(load(item))
        except ValueError as ex:
            logging.warning(ex)

    return rules
