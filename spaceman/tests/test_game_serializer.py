from django.test import TestCase
from game_api.serializers import GameSerializer

from django.core.exceptions import ValidationError

from unittest.mock import *
from game_api.random_words import RandomWord
from game_api.models import Game

from rest_framework.serializers import ModelSerializer, ValidationError

class GameSerializerTests( TestCase ):

    ### create
    def test_create_should_create_game_with_given_word( self ):
        game = GameSerializer().create( {'word': 'BALLOON'} )
        self.assertEqual( game.word, 'BALLOON')

    def test_create_should_pick_random_word_when_none_given( self ):
        with patch.object( RandomWord, 'getRandomWord' ) as mockGetRandomWord:
            mockGetRandomWord.return_value = 'TESTWORD'

            game = GameSerializer().create( {} )
            self.assertEqual( game.word, 'TESTWORD')

    def test_create_should_uppercase_word( self ):
        game = GameSerializer().create( {'word': 'balloon'} )
        self.assertEqual( game.word, 'BALLOON')

        with patch.object( RandomWord, 'getRandomWord' ) as mockGetRandomWord:
            mockGetRandomWord.return_value = 'randomballoon'

            game = GameSerializer().create( {} )
            self.assertEqual( game.word, 'RANDOMBALLOON')

    def test_create_should_init_guessed_word_state_to_be_empty_strings_for_each_word_char( self ):
        game = GameSerializer().create( {'word': 'BALLOON'} )

        self.assertEqual( len(game.guessed_word_state), len('BALLOON'))
        self.assertEqual( len( [c for c in game.guessed_word_state if c != ''] ), 0)



    ### update
    def test_update_should_call_handleGuess_with_guessed_letter( self ):
        mock_game = Mock( letters_available = ['A', 'B', 'C'] )
        request_data = { 'letters_guessed': 'B' } 

        serializer = GameSerializer()
        with patch.object( ModelSerializer, 'update' ) as mock_super_create:
            mock_super_create.return_value = None
            serializer.update( mock_game, request_data )
        
        mock_game.handleGuess.assert_called_with( 'B' )


    ## validating letters guessed
    def test_validate_letters_guessed_should_stop_guesses_when_game_over( self ):
        serializer = GameSerializer()
        serializer.instance = Mock( is_game_over = True )

        with self.assertRaises( ValidationError ):
            serializer.validate_letters_guessed( ['C'] )

    def test_validate_letters_guessed_should_raise_error_when_guess_is_not_single_letter( self ):
        serializer = GameSerializer()
        serializer.instance = Mock( )

        with self.assertRaises( ValidationError ):
            serializer.validate_letters_guessed( ['CAR'] )

    def test_validate_letters_guessed_should_raise_error_guess_is_repeated( self ):
        serializer = GameSerializer()
        serializer.instance = Mock( )

        with self.assertRaises( ValidationError ):
            serializer.validate_letters_guessed( ['C', 'C'] )
    
    def test_validate_letters_guessed_should_raise_error_when_guess_not_available( self ):
        serializer = GameSerializer()
        serializer.instance = Mock( letters_available = ['A', 'B'] )

        with self.assertRaises( ValidationError ):
            serializer.validate_letters_guessed( ['C'] )

    def test_validate_letters_guessed_should_return_valid_guess( self ):
        serializer = GameSerializer()
        serializer.instance = Mock( is_game_over = False, letters_available = ['A', 'B'] )

        self.assertEqual(['B'], serializer.validate_letters_guessed(['B']))





