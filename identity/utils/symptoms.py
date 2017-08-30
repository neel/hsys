import json
import copy
import os

# from identity.utils.symptoms import builder, decorator
# b = builder()
# sub = b.subtree([{'q': '1.1.1', 'a': '3 hours'}, {'q': '1.1.2', 'a': 'front'}, {'q': '1.1.3', 'a': 'back'}, {'q': '1.1.4', 'a': 'suddenly'}, {'q': '1.1.5', 'a': 'mild'}, {'q': '1.1.6', 'a': 'continous'}])
# decorator().decorate(sub, "en")

class vertex:
	def __init__(self, id, *args, **kwargs):
		self.name 	= id
		self.parent 	= None
		self.children 	= []
		self.type 	= kwargs.get('type', 	None)
		self.labels 	= kwargs.get('labels', 	None)
		self.title 	= kwargs.get('title', 	None)
		self.tags 	= kwargs.get('tags', 	None)
		self.answers	= kwargs.get('answers', None)
		self.order	= kwargs.get('order', 	None)
		self.rule	= kwargs.get('rule', 	None)
	def clone(self):
		v = vertex(self.name)
		v.parent 	= None
		v.children 	= []
		v.type 		= self.type
		v.labels 	= self.labels
		v.title 	= self.title
		v.tags 		= self.tags
		v.answers	= self.answers
		v.order		= self.order
		v.rule		= self.rule
		return v
	def append_child(self, node):
		node.parent = self
		self.children.append(node)
	
class builder(object):

	def __init__(self):
		self.dictionary = "symptoms.json"
		self.vertices 	= {}
		self.root 	= None
		self.symptoms 	= None
		self.parse()

	def parse(self):
		with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dictionary)) as io:
			self.symptoms = json.load(io)
		for elem in self.symptoms:
			id = str(elem['id'])
			p  = str(elem['parent'])
			try:
				eanswers = json.loads(elem['answers'])
			except:
				eanswers = []

			erule = {"_": {"en": {"orientation": "ab"}, "order": 0}} if type(elem['rule']) in [unicode, str] else elem['rule']

			v = vertex(id, 
					type=elem['type'], 
					labels={"en": elem['label_en'], "bn": elem["label_bn"]}, 
					title=elem['title_tag'], 
					tags={"en": elem['tag_en'], "bn": elem["tag_bn"]}, 
					answers=eanswers, 
					order=elem["order"], 
					rule=erule
			)

			self.vertices[id] = v
			if p in self.vertices:
				pelem = self.vertices[p]
				v.parent = pelem
				pelem.children.append(v)
		
			self.root = self.vertices['0']

	def write(self, path):
		class vertex_encoder(json.JSONEncoder):
			def default(self, obj):
				c = copy.copy(obj.__dict__)
				c.pop('parent', None)
				return c
		with open("symptoms-tree.json", 'w') as io:
			io.write(vertex_encoder().encode(self.root))	

	def subtree(self, table):
		tree = self.root
		croot = self.root.clone()
		answers_dict = {}
		visited = []
		def visit(node, a=None):
			if a is not None:
				node.answer = a
			if not node.name in visited:
				visited.append(node.name)
			if node.parent != None:
				visit(node.parent)
		
		def filter(cnode):
			node = self.vertices[cnode.name]
			for child in node.children:
				if child.name in visited:
					cchild = child.clone()
					if cchild.name in answers_dict:
						cchild.answer = answers_dict[cchild.name]
					cnode.append_child(cchild)
					filter(cchild)
		
		for row in table:
			q  = row['q']
			a  = row['a']
			qv = self.vertices[q]
			answers_dict[q] = a
			visit(qv, a)	

		filter(croot)
		return croot
		


# rules
# orientation: "" | ab | ba | a | b // a is the question tag, b is the answer
# {"_": {"en": {"orientation": "ab"}, "bn": {"orientation": "ba"}}}
# {"_": {"en": {"orientation": "ab"}}, "none": ""}
class decorator(object):
	def question(self, node, lang):
		def concat(q, a, orientation):
			q_r = '<div class="symptom-token symptom-question-tag">%s</div>' % q
			a_r = '<div class="symptom-token symptom-answer">%s</div>' % a
			if(orientation == "ab"):
				return q_r+a_r
			elif(orientation == "ba"):
				return a_r+q_r
			elif(orientation == "a"):
				return q_r
			elif(orientation == "b"):
				return a_r
			else:
				return ""

		rule = node.rule
		_ = rule['_'][lang]
		orientation = _['orientation']

		answer = node.answer
		if answer in rule:
			special = rule[answer]
			# there is no language specific rule, so assumes to be translated to constant in special
			if type(special) == str:
				return special
			else:
				special = special[lang]
				orientation = special.orientation

		return '<div class="symptom-token symptom-leaf" data-order="%s">%s</div>' % (node.order, concat(node.tags[lang], answer, orientation))


	def subcategory(self, node, lang):
		rule = node.rule
		_ = rule['_'][lang]
	
		chunk = {
			'order': node.order,
			'elem':  '<div class="symptom-token symptom-subcategory" data-order="%s">%s</div>' % (node.order, node.tags[lang])
		}

		chunks = []
		chunks.append(chunk)
		for child in node.children:
			chunks.append({
				'order': child.order,
				'elem': self.question(child, lang)
			})


		schunks = sorted(chunks, key=lambda k: float(k["order"]))
		print(schunks)
		elems  = [c['elem'] for c in schunks]
	 	return ''.join(elems)

		
	def category(self, node, lang):
		elems = []
		for child in node.children:
			elem = '<div class="symptom-block">%s</div>' % self.subcategory(child, lang)
			elems.append(elem)
		return ''.join(elems)

	def decorate(self, root, lang):
		elems = []
		for child in root.children:
			elem = self.category(child, lang)
			elems.append(elem)
		return ''.join(elems)
	
