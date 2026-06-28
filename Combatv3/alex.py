variable = "variable name"

list1  = [1, "2", 3, variable]

list1.append("orange")
list1.remove(1)
list1.pop()
#print(list1)
import random 

def add(x,y):
	return x + y
	
print(add(1,2))

input()

suits = ["Clubs" ,"Spades", "Hearts", "Diamonds"]
values = [9, 10, 11, 12, 13, 1]

class card:
	def __init__(self,suit,value):
		self.suit = suit
		self.value = value
		
	def face_changer(self):
		faceDictionary = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
		if self.value in faceDictionary:
			self.value = faceDictionary[self.value]
		return self

class deck:
	def __init__(self):
		self.dict = {"Clubs": [], "Spades" : [],"Hearts" : [], "Diamonds" : []}
		
	def generate(self):
		for value in values:
			for suit in suits:
				self.dict[suit].append(card(suit,value).face_changer())
		return self
				
			
			
class earth:
	def __init__(self, orientation):
		self.orientation = orientation
		self.people = []

class character:
	def __init__(self,card):
		self.card = card
		self.holding = self.card
		
card = card(random.choice(values),random.choice(suits))
character = character(card)
print(character.holding)
earth = earth("")
earth.people.append(character)
for character in earth.people:
	print(character)
	print(character.holding)

deck = deck()
deck.generate()

import pandas as pd
collector = []
for key in deck.dict:
	print(key)
	for x in deck.dict[key]:
		collector.append([x.value, x.suit])
df = pd.DataFrame(collector, columns= ["Value","Suit"])
df.to_csv(r"C:\Users\Matt\OneDrive\Desktop\alex\stuff.csv", index = False)
		
for i in deck.dict:
	print(i, len(deck.dict[i]))
	print([(x.suit, x.value) for x in deck.dict[i]])
	