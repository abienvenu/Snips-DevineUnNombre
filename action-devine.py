#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions


def start_guess_number():
    number = 12
    return ("Ok, essaie de deviner le nombre auquel je pense", number)


def try_number(number, guess):
    if guess == number:
        return "Bravo, tu as trouvé, c'était bien {}".format(number)
    elif guess < number:
        return "Non, c'est plus"
    else:
        return "Non, c'est moins"


def intent_callback(hermes, intentMessage):
    intent_name = intentMessage.intent.intent_name.replace("abienvenu:", "")
    result = None
    if intent_name == "startGuessNumber":
        (result, number) = start_guess_number()
    elif intent_name == "tryNumber":
        result = try_number(intentMessage.slots.Guess.first().value, number)

    if result is not None:
        hermes.publish_end_session(intentMessage.session_id, result)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
