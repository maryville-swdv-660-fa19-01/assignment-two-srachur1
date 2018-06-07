from rest_framework import serializers
from .models import Game

from .random_words import RandomWord 

class GameSerializer( serializers.ModelSerializer ):
    class Meta:
        model = Game
        exclude = ('word',)

    def create( self, validated_data ):
        if not validated_data.get('word'):
            validated_data['word'] = RandomWord.getRandomWord( min_length= 3)
        
        validated_data['word'] = validated_data.get('word').upper()
        
        validated_data['guessed_word_state'] = [''] * len( validated_data.get('word') ) 
        return super().create( validated_data )

    def update( self, instance, validated_data ):
        guessed_letter = self.__getGuessedLetterFromUpdate( instance.letters_available, validated_data.get('letters_guessed') )
        instance.handleGuess( guessed_letter )

        return super().update( instance, {} )

    def validate_is_game_over( self, data ):
        if self.instance and self.instance.is_game_over:
            raise serializers.ValidationError('Game is over!')
        return data

    def validate( self, data ):
        # Don't allow updates if game is over
        self.validate_is_game_over( data )
        return data

    def validate_letters_guessed( self, updated_letters_guessed ):
        # Don't allow guessing if game is over
        self.validate_is_game_over( updated_letters_guessed )

        # Validate the guess must be a single letter
        for c in updated_letters_guessed:
            if len(c) != 1:
                 raise serializers.ValidationError("'{}' is not a valid guess.".format( c )) 

        # Validate the guess does not already existin the guessed letters
        if len(updated_letters_guessed) != len( set( updated_letters_guessed ) ):
            raise serializers.ValidationError('Guess is not unique.') 

        # Validate the guessed letters was an available letters, and implicitly there was only one letter guessed
        if not self.__getGuessedLetterFromUpdate( self.instance.letters_available, updated_letters_guessed ):
            raise serializers.ValidationError('Guess is not valid.')
        return updated_letters_guessed

    
    def __getGuessedLetterFromUpdate( self, letters_available, updated_guessed_letters):
        """
        Returns the letter present in both the guessed letters and the available letters to guess. If more than
        one letter is present in both then this returns None as the guess would be invalid.
        """
        guessedLetters = set( letters_available ) & set( updated_guessed_letters )
        if len( guessedLetters ) == 1:
            return guessedLetters.pop()
        else:
            return None

class GameSolutionSerializer( serializers.ModelSerializer ):
    solution = serializers.CharField(source='word')

    class Meta:
        model = Game
        fields = ('solution',)
