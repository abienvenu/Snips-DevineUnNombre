#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from random import randint

secretNumber = {'value': 0}


def start_guess_number(slots):
    maxNumber = slots.Guess.first().value
    secretNumber['value'] = randint(1, maxNumber)
    return "Ok, essaie de deviner le nombre auquel je pense"


def try_number(hermes, intent_message):
    guess = intent_message.slots.Guess.first().value
    number = secretNumber['value']
    if guess == number:
        sentence = "Bravo, tu as trouvé, c'était bien {}".format(number)
        hermes.publish_end_session(intent_message.session_id, sentence)
    elif guess < number:
        return "Non, c'est plus"
    else:
        return "Non, c'est moins"


def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("abienvenu:", "")
    result = None
    if intent_name == "startGuessNumber":
        sentence = start_guess_number(intent_message.slots)
    elif intent_name == "tryNumber":
        sentence = try_number(hermes, intent_message)
    elif intent_name == "stopGuessNumber":
        sentence = "Ok, on arrête de jouer"
        hermes.publish_end_session(intent_message.session_id, sentence)

    if result is not None:
        hermes.publish_continue_session(
            intent_message.session_id,
            sentence
        )


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
