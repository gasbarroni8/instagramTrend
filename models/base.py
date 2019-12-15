

class Base():

	def __init__(self):
		pass

	def removListDuplicate(self, oldList):

		newList = []
		newList = list(set(oldList))
		newList.sort(key=oldList.index)

		return newList