#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from random import randint

secretNumber = {'value': 0}


def humaniser(nombre):
    nombre = round(nombre, 4)
    if str(nombre)[-2:] == ".0":
        nombre = int(nombre)
    return nombre


def start_guess_number(slots):
    minNumber = 1
    maxNumber = 30
    if slots.Min.first():
        minNumber = humaniser(slots.Min.first().value)
    if slots.Max.first():
        maxNumber = humaniser(slots.Max.first().value)
    secretNumber['value'] = randint(minNumber, maxNumber)
    return "Je pense à un nombre entre 1 et {}, essaie de deviner lequel".\
        format(maxNumber)


def try_number(hermes, intent_message):
    guess = humaniser(intent_message.slots.Guess.first().value)
    number = secretNumber['value']
    if guess == number:
        sentence = "Bravo, tu as trouvé, c'était bien {}!\
        À quand la prochaine partie ?".format(number)
        hermes.publish_end_session(intent_message.session_id, sentence)
    elif guess < number:
        return "Non, c'est plusse que {}".format(guess)
    else:
        return "Non, c'est moins que {}".format(guess)


def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("abienvenu:", "")
    sentence = None
    if intent_name == "startGuessNumber":
        sentence = start_guess_number(intent_message.slots)
    elif intent_name == "tryNumber":
        sentence = try_number(hermes, intent_message)
    elif intent_name == "stopGuessNumber":
        sentence = "Le nombre à deviner était {}. \
        J'espère qu'on rejouera bientôt.".format(secretNumber['value'])
        hermes.publish_end_session(intent_message.session_id, sentence)

    if sentence is not None:
        hermes.publish_continue_session(
            intent_message.session_id,
            sentence,
            ["abienvenu:tryNumber", "abienvenu:stopGuessNumber"]
        )


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
