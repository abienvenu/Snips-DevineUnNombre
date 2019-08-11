#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology.dialogue import DialogueConfiguration
from random import randint

INTENT_START = "abienvenu:startGuessNumber"
INTENT_STOP = "abienvenu:cancelGame"
INTENT_TRY = "abienvenu:tryNumber"

state = {
    'started': False,
    'secret': None
}


def enable_intents(hermes, intents):
    dialogue_conf = DialogueConfiguration().enable_intents(intents)
    hermes.configure_dialogue(dialogue_conf)


def disable_intents(hermes, intents):
    dialogue_conf = DialogueConfiguration().disable_intents(intents)
    hermes.configure_dialogue(dialogue_conf)


def humaniser(nombre):
    nombre = round(nombre, 4)
    if str(nombre)[-2:] == ".0":
        nombre = int(nombre)
    return nombre


def start_game(hermes, intent_message):
    state['started'] = True
    minNumber = 1
    maxNumber = 30
    slots = intent_message.slots
    if slots.Min.first():
        minNumber = humaniser(slots.Min.first().value)
    if slots.Max.first():
        maxNumber = humaniser(slots.Max.first().value)
    if maxNumber <= 2:
        maxNumber = 2
    if minNumber >= maxNumber:
        minNumber = 1
    state['secret'] = randint(minNumber, maxNumber)

    enable_intents(hermes, [INTENT_STOP, INTENT_TRY])
    phrase = "Je pense à un nombre entre {} et {}, essaie de deviner lequel"\
        .format(minNumber, maxNumber)
    hermes.publish_continue_session(
        intent_message.session_id,
        phrase,
        [INTENT_TRY, INTENT_STOP]
    )


def try_number(hermes, intent_message):
    guess = humaniser(intent_message.slots.Guess.first().value)
    number = state['secret']
    if guess == number:
        phrase = "Bravo, tu as trouvé, c'était bien {}!\
        À quand la prochaine partie ?".format(number)
        stop_guess_number(hermes, intent_message, phrase)
    else:
        if guess < number:
            phrase = "Non, c'est + que {}".format(guess)
        else:
            phrase = "Non, c'est moins que {}".format(guess)
        hermes.publish_continue_session(
            intent_message.session_id,
            phrase,
            [INTENT_TRY, INTENT_STOP]
        )


def stop_game(hermes, intent_message):
    phrase = "Le nombre à deviner était {}. \
        J'espère qu'on rejouera bientôt.".format(state['secret'])
    stop_guess_number(hermes, intent_message, phrase)


def stop_guess_number(hermes, intent_message, phrase):
    state['started'] = False
    disable_intents(hermes, [INTENT_STOP, INTENT_TRY])
    hermes.publish_end_session(intent_message.session_id, phrase)


def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name
    if intent_name == INTENT_START:
        start_game(hermes, intent_message)
    elif state['started']:
        if intent_name == INTENT_TRY:
            try_number(hermes, intent_message)
        elif intent_name == INTENT_STOP:
            stop_game(hermes, intent_message)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
