import json
import copy
import pdb

vertices = {}

class vertex_encoder(json.JSONEncoder):
	def default(self, obj):
		c = copy.copy(obj.__dict__)
		c.pop('parent', None)
		return c

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
		
with open("symptoms.json") as io:
	symptoms = json.load(io)
	
# symptoms table to symptoms tree
for elem in symptoms:
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

	vertices[id] = v
	if p in vertices:
		pelem = vertices[p]
		v.parent = pelem
		pelem.children.append(v)
		
root = vertices['0']

with open("symptoms-tree.json", 'w') as io:
	io.write(vertex_encoder().encode(root))
	
tree = root

def subtree(table):
	croot = root.clone()
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
		node = vertices[cnode.name]
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
		qv = vertices[q]
		answers_dict[q] = a
		visit(qv, a)	
	
	filter(croot)
	return croot
		
# rules
# orientation: "" | ab | ba | a | b // a is the question tag, b is the answer
# {"_": {"en": {"orientation": "ab"}, "bn": {"orientation": "ba"}}}
# {"_": {"en": {"orientation": "ab"}}, "none": ""}
def question_decorator(node, lang):
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


def subcategory_decorator(node, lang):
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
			'elem': question_decorator(child, lang)
		})


	schunks = sorted(chunks, key=lambda k: float(k["order"]))
	print(schunks)
	elems  = [c['elem'] for c in schunks]
 	return ''.join(elems)

		
def category_decorator(node, lang):
	elems = []
	for child in node.children:
		elem = '<div class="symptom-block">%s</div>' % subcategory_decorator(child, lang)
		elems.append(elem)
	return ''.join(elems)

def decorate(root, lang):
	elems = []
	for child in root.children:
		elem = category_decorator(child, lang)
		elems.append(elem)
	return ''.join(elems)
	
