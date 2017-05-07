#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from telegram.ext import Updater, Dispatcher, CommandHandler
from itertools import permutations
import random

TOKEN = ""

code_set = set(''.join(i) for i in permutations('1234567890', 4))
code_tuple = tuple(code_set)
answer_list = (
    "I think, the number is `{0}`",
    "Is it `{0}`?",
    "It's definitely `{0}`",
    "I'm not sure, but it could be `{0}`",
    "It got it, the number is `{0}`",
    "It's too early to be 100% sure, but the number `{0}` seems quite suspicious to me.",
    "This one is easy: `{0}`",
    "I'm capable of reading your thoughts, but our astral connection is weak. "\
    "You are either thinking of Shrek or `{0}`",
    "Stop right there, criminal scum! Pay the court a fine or serve your sentence, your stolen `{0}` is now forfeit",
    "I used to be an adventurer like you, then I took an `{0}` in the knee.",
    "`{0}`. `{0}`! `{0}`?")


def bc(code, guess):
    a = [0, 0]
    for i in range(0, 4):
        if guess[i] == code[i]:
            a[0] += 1
        elif guess[i] in code:
            a[1] += 1
    return a


def start(bot, update, chat_data):
    update.message.reply_text(
        'I\'m a bot for the Bulls and Cows game.\n'
        'To get a list of possible commands, please type `/help`', parse_mode='Markdown')


def start_game(bot, update, chat_data):
    message = update.message.text.split()
    if len(message) != 2:
        update.message.reply_text('Usage: `/start_game <guess|hide>`', parse_mode='Markdown')
        return
    if chat_data.get('in_progress') == 1:
        update.message.reply_text(
            'There is already a game in progress.\n'
            'If you really want to abandon current game, please use `/end_game`.', parse_mode='Markdown')
        return
    if message[1] == 'guess':
        chat_data['in_progress'] = 1
        chat_data['gamemode'] = 'guess'
        chat_data['number'] = random.choice(code_tuple)
        chat_data['guesses'] = 0
        update.message.reply_text(
            'A random 4-digit number without repeating digits was picked.\n'
            'To make a guess, use `/ask <number>`', parse_mode='Markdown')
    if message[1] == 'hide':
        chat_data['in_progress'] = 1
        chat_data['gamemode'] = 'hide'
        chat_data['codes'] = code_set.copy()
        chat_data['guesses'] = 1
        update.message.reply_text(
            'Think of a 4-digit number without repeating digits.\n'
            'You\'ll have to give a number of bulls and cows for every guess I made.'
            'To give an answer, use `/answer <bulls> <cows>`', parse_mode='Markdown')
        code = random.choice(code_tuple)
        update.message.reply_text("Okay, let's begin with `{0}`".format(code), parse_mode='Markdown')
        chat_data.get('codes').remove(code)
        chat_data["last_code"] = code
    else:
        update.message.reply_text('Usage: `/start_game <"guess"|"hide">`', parse_mode='Markdown')


def ask(bot, update, chat_data):
    if chat_data.get('in_progress') != 1 or chat_data.get('gamemode') != 'guess':
        update.message.reply_text(
            'This command should be used in `guess` gamemode.\n'
            'Type `/start_game guess`', parse_mode='Markdown')
        return
    message = update.message.text.split()
    if len(message) != 2 or len(message[1]) != 4 or not message[1].isdigit():
        update.message.reply_text('Please, type a 4-digit number')
        return
    number = message[1]
    chat_data['guesses'] += 1
    bulls, cows = bc(chat_data['number'], number)
    if bulls == 4:
        chat_data['in_progress'] = 0
        update.message.reply_text(
            'You have guessed the number!\n'
            + 'It took you ' + str(chat_data['guesses']) + ' '
            + ('guesses.', 'guess! Impossible!')[chat_data['guesses'] == 1])
    else:
        update.message.reply_text(
            'Bulls: ' + str(bulls)
            + '\nCows: ' + str(cows))


def answer(bot, update, chat_data):
    if chat_data.get('in_progress') != 1 or chat_data.get('gamemode') != 'hide':
        update.message.reply_text(
            'This command should be used in `hide` gamemode.\n'
            'Type `/start_game hide`', parse_mode='Markdown')
        return
    message = update.message.text.split()
    if len(message) != 3 or not message[1].isdigit() or not message[2].isdigit():
        update.message.reply_text('Please, type two numbers')
        return
    bulls, cows = int(message[1]), int(message[2])
    if bulls not in range(0, 5) or cows not in range(0, 5):
        update.message.reply_text('The numbers must be in range [0, 4]')
        return
    if bulls == 4:
        chat_data['in_progress'] = 0
        update.message.reply_text(
            'I have guessed your number!\n'
            'It took me ' + str(chat_data['guesses']) + ' '
            + ('guesses.', 'guess! GERMAN SCIENCE IS THE BEST IN THE WORLD!')[chat_data['guesses'] == 1])
    else:
        for code in chat_data.get('codes').copy():
            if [bulls, cows] != bc(code, chat_data.get('last_code')):
                chat_data.get('codes').remove(code)
        if len(chat_data.get('codes')):
            code = chat_data.get('codes').pop()
            chat_data['last_code'] = code
            chat_data['guesses'] += 1
            update.message.reply_text(random.choice(answer_list).format(code), parse_mode='Markdown')
        else:
            update.message.reply_text(
                'Your answers are contradictive.\n'
                'Try being less of a liar next time.\n'
                'It took me ' + str(chat_data['guesses']) + ' '
                + ('guesses', 'guess')[chat_data['guesses'] == 1]
                + ' to find out that you were wasting my time.')


def end_game(bot, update, chat_data):
    if chat_data.get('in_progress') != 1:
        update.message.reply_text('There is no game in progress')
        return
    chat_data['in_progress'] = 0
    update.message.reply_text('You have left the game.')
    if chat_data['gamemode'] == 'guess':
        update.message.reply_text('The number was: ' + chat_data['number'])


def bot_help(bot, update):
    update.message.reply_text(
        'Available commands:\n'
        '`/start_game <"guess"|"hide">` - starts game in selected mode\n'
        '`/ask <4-digit number>` - try to guess the number in `guess` mode\n'
        '`/answer <bulls> <cows>` - tell the amount of bulls and cows in `hide` mode\n'
        '`/end_game` - ends current game, allowing to begin a new one', parse_mode='Markdown')


def main():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('start_game', start_game, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('ask', ask, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('answer', answer, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('end_game', end_game, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('help', bot_help))

    updater.start_polling()

    updater.idle()


main()
