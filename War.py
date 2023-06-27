import pygame
import random
from test import *
import time

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.face_up = False  # track whether the card is face up or face down

class CardGameObject(GameObject):
    def __init__(self, game, card, pos_x, pos_y, is_war_cause_card=False, player=None, is_extra_face_up_card=False):
        super().__init__(game.makeSpriteImage(f'cards/{card.suit}{card.value}.jpg' if card.face_up else 'cards/TOP.jpg'))
        self.card = card
        self.rect.center = (pos_x, pos_y)  # Changed to center the card
        self.is_war_cause_card = is_war_cause_card  # track whether the card is a war cause card
        self.player = player
        self.is_extra_face_up_card = is_extra_face_up_card
        #print(f"{self.player.name} played card with value {self.card.value}")  # Print the card value as soon as it is displayed

    def flip_card(self, game):  # method to flip the card
        self.image = game.makeSpriteImage(f'cards/{self.card.suit}{self.card.value}.jpg' if self.card.face_up else 'cards/TOP.jpg')

class Deck:
    def __init__(self):
        self.cards = []
        self.populate()

    def populate(self):
        suits = ['CLUBS', 'DIAMONDS', 'HEARTS', 'SPADES']
        for value in range(2, 5):  # values from 1 to 14, where 14 represents the ace
            for suit in suits:
                self.cards.append(Card(suit, value))
        
        for suit in suits:
            for value in range(5, 15):  # values from 1 to 14, where 14 represents the ace
                self.cards.append(Card(suit, value))

    def shuffle(self):
        #random.shuffle(self.cards)
        for card in self.cards:  # Ensure all cards are face up after shuffling
            card.face_up = True

    def deal(self):
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.won_cards = []

    def take_card(self, card):
        self.hand.append(card)

    def play_card(self, face_up=True):
        if self.hand:
            card = self.hand.pop()
            card.face_up = face_up  # specify whether the card is face up or face down
            if not self.hand and self.won_cards:  # reshuffle won cards if hand is empty
                print("Reshuffling cards!")
                self.hand = self.won_cards
                self.won_cards = []
                self.shuffle_hand()
            return card
        if not self.hand and self.won_cards:
            print("Reshuffling cards!")
            self.hand = self.won_cards
            self.won_cards = []
            self.shuffle_hand()
        print("No cards left in hand!")
        return None

    def place_card_face_down(self):
        return self.play_card(False)  # the card is face down

    def shuffle_hand(self):
        random.shuffle(self.hand)
        for card in self.hand:  # Ensure all cards are face up after shuffling
            card.face_up = True

class WarGame(Game):
    def __init__(self, windowWidth, windowHeight):
        super().__init__(windowWidth, windowHeight)
        self.room = Room('War', self.makeBackground((0, 0, 0)))  # make a black background
        self.addRoom(self.room)
        self.player1 = Player('Opponent')
        self.player2 = Player('You')
        self.deck = Deck()
        self.deck.shuffle()
        self.cards_in_play = []
        self.turn_over = False
        self.war = False
        self.war_cards = []
        self.total_cards_played = 0  # Initialize total cards played
        
        # Create a font
        self.font = self.makeFont('Arial', 20)

        # Create a TextRectangle for each player
        self.player1_text = TextRectangle(f'{self.player1.name}: 0 cards won', 100, 40, self.font, (255, 255, 255))
        self.player2_text = TextRectangle(f'{self.player2.name}: 0 cards won', 100, windowHeight - 60, self.font, (255, 255, 255))

        # Create a TextRectangle for each player's remaining cards
        self.player1_remaining_text = TextRectangle(f'{self.player1.name}: {len(self.player1.hand)} cards left', 100, 60, self.font, (255, 255, 255))
        self.player2_remaining_text = TextRectangle(f'{self.player2.name}: {len(self.player2.hand)} cards left', 100, windowHeight - 30, self.font, (255, 255, 255))

        self.deal_cards()  # Moved this line after the creation of player1_text and player2_text

    def deal_cards(self):
        total_cards_dealt = 0
        while len(self.deck.cards) > 0:
            card = self.deck.deal()
            card.face_up = True  # Set the initial deal to face-up
            self.player1.take_card(card)
            total_cards_dealt += 1
            card = self.deck.deal()
            card.face_up = True  # Set the initial deal to face-up
            self.player2.take_card(card)
            total_cards_dealt += 1
        print(f"Total cards dealt: {total_cards_dealt}")
        self.draw_cards()

    def draw_cards(self, draw_new = True):
        self.room.roomObjects.empty()  # Remove all objects from the room
        # print(f"Total cards played: {self.total_cards_played}")  # Print total cards played at the start of each turn
        # Draw only the top card of each player's hand
        if draw_new:
            if self.player1.hand:
                card_object = CardGameObject(self, self.player1.hand[-1], self.windowWidth // 2, self.windowHeight // 2 - 75, player=self.player1)  # Changed the y-coordinate to add space between the cards
                self.room.addObject(card_object)
            else:
                print("--------------------------- ERROR ---------------------------")
            if self.player2.hand:
                card_object = CardGameObject(self, self.player2.hand[-1], self.windowWidth // 2, self.windowHeight // 2 + 75, player=self.player2)  # Changed the y-coordinate to add space between the cards
                self.room.addObject(card_object)

        # Draw the war cards if in war
        if self.war:
            offset = 75
            player1_offset = offset  # Offsets for the cards of player 1
            player2_offset = offset  # Offsets for the cards of player 2
            for card_object in self.war_cards:
                self.room.addObject(card_object)
                print(card_object.card.face_up, card_object.rect.center, card_object.is_war_cause_card, card_object.player, card_object.is_extra_face_up_card)
                if not card_object.is_war_cause_card:  # Only set the position if this is not a war cause card
                    if card_object.player == self.player1:
                        if card_object.is_extra_face_up_card:  # If the card is the extra face-up card
                            card_object.rect.center = (self.windowWidth // 2 - player1_offset - 0, self.windowHeight // 2 - 75)
                            player1_offset += 75
                        else:
                            card_object.rect.center = (self.windowWidth // 2 - player1_offset, self.windowHeight // 2 - 75)
                            player1_offset += 30
                    elif card_object.player == self.player2:
                        if card_object.is_extra_face_up_card:  # If the card is the extra face-up card
                            card_object.rect.center = (self.windowWidth // 2 + player2_offset + 0, self.windowHeight // 2 + 75)
                            player2_offset += 75
                        else:
                            card_object.rect.center = (self.windowWidth // 2 + player2_offset, self.windowHeight // 2 + 75)
                            player2_offset += 30

        
        self.player1_text.setText(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
        self.player2_text.setText(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')

        # Add the TextRectangles to the room
        self.room.addObject(self.player1_text)
        self.room.addObject(self.player2_text)

        # Update and add the TextRectangles for remaining cards
        self.player1_remaining_text.setText(f'{self.player1.name}: {len(self.player1.hand)} cards left')
        self.player2_remaining_text.setText(f'{self.player2.name}: {len(self.player2.hand)} cards left')
        #print(f'{self.player1.name}: {len(self.player1.hand)} cards left, {self.player2.name}: {len(self.player2.hand)} cards left')  # Print the updated remaining cards text
        self.room.addObject(self.player1_remaining_text)
        self.room.addObject(self.player2_remaining_text)

    def play_round(self):
        if not self.turn_over:
            card1 = self.player1.play_card()
            card2 = self.player2.play_card()
            draw_new = True
            if card1 and card2:  # if both players have cards to play
                self.cards_in_play.extend([card1, card2])
                self.total_cards_played += 2  # Increase total cards played by 2
                if card1.value > card2.value:
                    self.player1.won_cards.extend(self.cards_in_play)
                    self.cards_in_play = []
                    self.turn_over = True
                    self.war = False
                    # Update player 1's TextRectangle
                    self.player1_text.setText(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                    #print(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                    self.draw_cards(draw_new = draw_new)
                elif card1.value < card2.value:
                    self.player2.won_cards.extend(self.cards_in_play)
                    self.cards_in_play = []
                    self.turn_over = True
                    self.war = False
                    # Update player 2's TextRectangle
                    self.player2_text.setText(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                    #print(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                    self.draw_cards(draw_new = draw_new)
                else:
                    print("WAR!")
                    self.war = True
                    draw_new = False
                    war_cause_cards = [card1, card2]  # save the cards that caused the war
                    self.war_cards.clear()  # clear old war cards
                    self.cards_in_play = []

                    for card in war_cause_cards:
                            card_object = CardGameObject(self, card, self.windowWidth // 2, self.windowHeight // 2 - 75 if card == card1 else self.windowHeight // 2 + 75, is_war_cause_card=True, player=self.player1 if card == card1 else self.player2)
                            self.war_cards.append(card_object)
                            self.cards_in_play.append(card)
                    
                    t = 2
                    while t:
                        t -= 1
                        # add the cards that caused the war back to the war_cards

                        for _ in range(3):  # place three cards face down
                            if self.player1.hand:
                                card = self.player1.place_card_face_down()
                                card_object = CardGameObject(self, card, self.windowWidth // 2, self.windowHeight // 2 - 75, player=self.player1)  # Set the position of war_cause_cards to the default card piles
                                self.war_cards.append(card_object)
                                self.cards_in_play.append(card)  # Add the face-down cards to self.cards_in_play
                                self.total_cards_played += 1  # Increase total cards played by 1
                            else:
                                print("Player 1 doesn't have enough cards to complete the war")
                                # Player 1 doesn't have enough cards to complete the war
                                self.player2.won_cards.extend(self.cards_in_play)
                                self.cards_in_play = []
                                self.turn_over = True
                                self.war = False
                                # Update player 2's TextRectangle
                                self.player2_text.setText(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                                print(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                                return
                            if self.player2.hand:
                                card = self.player2.place_card_face_down()
                                card_object = CardGameObject(self, card, self.windowWidth // 2, self.windowHeight // 2 + 75, player=self.player2)  # Set the position of war_cause_cards to the default card piles
                                self.war_cards.append(card_object)
                                self.cards_in_play.append(card)  # Add the face-down cards to self.cards_in_play
                                self.total_cards_played += 1  # Increase total cards played by 1
                            else:
                                print("Player 2 doesn't have enough cards to complete the war")
                                # Player 2 doesn't have enough cards to complete the war
                                self.player1.won_cards.extend(self.cards_in_play)
                                self.cards_in_play = []
                                self.turn_over = True
                                self.war = False
                                # Update player 1's TextRectangle
                                self.player1_text.setText(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                                print(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                                return
                        # add one more card face up from each player
                        if self.player1.hand:
                            card1 = self.player1.play_card(face_up=True)
                            card_object = CardGameObject(self, card1, 0, 0, is_war_cause_card=False, player=self.player1, is_extra_face_up_card=True)  # Set the position of war_cause_cards to the default card piles
                            self.war_cards.append(card_object)
                            self.cards_in_play.append(card1)
                            self.total_cards_played += 1  # Increase total cards played by 1
                        else:
                            print("Player 1 doesn't have enough cards to complete the war")
                            # Player 1 doesn't have enough cards to complete the war
                            self.player2.won_cards.extend(self.cards_in_play)
                            self.cards_in_play = []
                            self.turn_over = True
                            self.war = False
                            # Update player 2's TextRectangle
                            self.player2_text.setText(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                            print(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                            return
                        if self.player2.hand:
                            card2 = self.player2.play_card(face_up=True)
                            card_object = CardGameObject(self, card2, 0, 0, is_war_cause_card=False, player=self.player2, is_extra_face_up_card=True)  # Set the position of war_cause_cards to the default card piles
                            self.war_cards.append(card_object)
                            self.cards_in_play.append(card2)
                            self.total_cards_played += 1  # Increase total cards played by 1
                        else:
                            print("Player 2 doesn't have enough cards to complete the war")
                            # Player 2 doesn't have enough cards to complete the war
                            self.player1.won_cards.extend(self.cards_in_play)
                            self.cards_in_play = []
                            self.turn_over = True
                            self.war = False
                            # Update player 1's TextRectangle
                            self.player1_text.setText(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                            print(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                            return

                        self.draw_cards(draw_new = draw_new)

                        print(f'WAR: Player 1: {card1.value} vs. Player 2: {card2.value}')
                        # Determine the winner of the war
                        if card1.value > card2.value:
                            self.player1.won_cards.extend(self.cards_in_play)
                            self.cards_in_play = []
                            self.turn_over = True
                            self.war = False
                            # Update player 1's TextRectangle
                            self.player1_text.setText(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                            print(f'{self.player1.name}: {len(self.player1.won_cards)} cards won')
                            return
                        elif card1.value < card2.value:
                            self.player2.won_cards.extend(self.cards_in_play)
                            self.cards_in_play = []
                            self.turn_over = True
                            self.war = False
                            # Update player 2's TextRectangle
                            self.player2_text.setText(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                            print(f'{self.player2.name}: {len(self.player2.won_cards)} cards won')
                            return
                        else:
                            print("ANOTHER WAR!")
                            self.war = True
                            # self.war_cards[-1]
                            # self.war = True
                            # self.turn_over = False
                            # self.war_cards.clear()  # clear old war cards
                            # self.cards_in_play = []
        else:
            self.turn_over = False
            self.war_cards.clear()

    def run(self):
        self.start()
        
        font = self.makeFont('Arial', 30)
        win_text = TextRectangle(f'{self.player1.name} is the winner!', self.windowWidth // 2 - 150 , self.windowHeight // 2 - 10, font, (255, 0, 0))
        win_text.rect.center = (self.windowWidth // 2, self.windowHeight // 2)
        #self.room.addObject(win_text)
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.play_round()
                    if len(self.player1.won_cards) + len(self.player1.hand) == 52:
                        print(f"{self.player1.name} is the winner!")
                        win_text.setText(f"{self.player1.name} is the winner!")
                        self.room.addObject(win_text)
                    elif len(self.player2.won_cards) + len(self.player2.hand) == 52:
                        print(f"{self.player2.name} is the winner!")
                        win_text.setText(f"{self.player2.name} is the winner!")
                        self.room.addObject(win_text)
                    
            self.room.updateObjects()
            self.room.renderBackground(self)
            self.room.renderObjects(self)
            pygame.display.flip()
            self.clock.tick(10)
        pygame.quit()

if __name__ == "__main__":
    game = WarGame(1200, 600)
    game.run()