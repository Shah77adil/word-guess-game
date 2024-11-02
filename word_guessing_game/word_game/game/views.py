# game/views.py
from django.shortcuts import render, redirect
import requests
import random

def start_game(request):
    # Fetch a random word from the API with different lengths for difficulty
    difficulty = request.GET.get('difficulty', 'easy')
    word_length = {'easy': 4, 'medium': 6, 'hard': 8}.get(difficulty, 4)
    try:
        response = requests.get(f"https://random-word-api.herokuapp.com/word?number=1&length={word_length}")
        response.raise_for_status()  # Ensure the request was successful
        word = response.json()[0]
    except requests.RequestException:
        word = "default"  # Fallback word if the API fails

    # Hide random letters in the chosen word
    hidden_word = hide_letters(word)

    # Initialize game session data
    request.session['word'] = word
    request.session['hidden_word'] = hidden_word
    request.session['attempts'] = 5  # Set max attempts
    request.session['score'] = 0

    return render(request, 'game/index.html', {
        'hidden_word': hidden_word,
        'attempts': request.session['attempts'],
        'score': request.session['score'],
        'message': "Start guessing the missing letters!",
        'difficulty': difficulty,
    })

def hide_letters(word):
    indices_to_hide = random.sample(range(len(word)), min(3, len(word)))
    return ''.join('_' if i in indices_to_hide else letter for i, letter in enumerate(word))

def guess_letter(request):
    # Game logic for processing guesses
    word = request.session.get('word')
    hidden_word = list(request.session.get('hidden_word'))
    guess = request.POST.get("guess", "").lower()

    message = ""
    reset_game = False

    if guess in word:
        # Reveal guessed letters
        for i, letter in enumerate(word):
            if letter == guess:
                hidden_word[i] = letter
        request.session['hidden_word'] = ''.join(hidden_word)

        # Check if word is fully guessed
        if '_' not in hidden_word:
            request.session['score'] += 10  # Increment score
            message = "Well done! You've guessed the word!"
            reset_game = True
        else:
            message = "Good guess!"
    else:
        # Decrement attempts if incorrect guess
        request.session['attempts'] -= 1
        if request.session['attempts'] <= 0:
            message = f"Out of attempts! The word was '{word}'. Try again!"
            reset_game = True
        else:
            message = "Incorrect guess. Try again!"

    # Update session and render page with updated info
    return render(request, 'game/index.html', {
        'hidden_word': ''.join(hidden_word),
        'message': message,
        'attempts': request.session['attempts'],
        'score': request.session['score'],
        'reset_game': reset_game,
    })
