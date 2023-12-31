#######################################
# CONSTANTS
#######################################
import re
WORD_REGEX = re.compile(r'[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*')


DIGITS = '0123456789'

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_CLASS='CLASS'
TT_EXTENDS='EXTENDS'
TT_MOD='TT_MOD'
TT_LBRACE='LBRACE'
TT_RBRACE='RBRACE'
TT_ASSIGN='ASSIGN'
TT_STATIC='STATIC'
TT_PROTECTED='PROTECTED'
TT_PUBLIC='PUBLIC'
TT_PRIVATE='PRIVATE'
TT_INT_CONST='INT_CONST'
TT_FLOAT_CONST='FLOAT_CONST'
TT_NEW='TT_NEW'
TT_ASSIGN='ASSIGN'
TT_GE='GE'
TT_SM='SM'
TT_ID='ID'
TT_THIS='TT_THIS'
TT_IF='IF'
TT_ELSE='ELSE'
TT_WHILE='WHILE'
TT_FOR='FOR'
TT_FUNCTION='TT_FUNCTION'
TT_RETURN='RETURN'
TT_NULL='NULL'
TT_NEW='NEW'
TT_BIT_AND='BIT_AND'
TT_BIT_OR='BIT_OR'
TT_BIT_XOR='BIT_XOR'
TT_BIT_NOT='BIT-NOT'
TT_STRING='BIT_STRING'
TT_RSHIFT='RSHIFT'
TT_LSHIFT='TT_LSHIFT'
TT_SINGLE_LINE_COMMENT='SINGLE_LINE_COMMENT'
TT_MULTI_LINE_COMMENT='MULTI_LINE_COMMENT'
TT_COMMA='COMMA'
TT_SEMICOLON='SEMICOLON'
TT_WORD = 'WORD'
TT_LINE = 'LINE'
TT_SPACE = 'SPACE'
TT_TAB = 'TAB'
TT_DATE = 'DATE'
TT_ODD = 'ODD'
TT_EVEN = 'EVEN'
TT_DIGIT = 'DIGIT'  # Add this line


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
#######################################
# NODES
#######################################

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

		self.pos_start = self.tok.pos_start
		self.pos_end = self.tok.pos_end

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

		self.pos_start = self.left_node.pos_start
		self.pos_end = self.right_node.pos_end

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		self.pos_start = self.op_tok.pos_start
		self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'
#######################################
# PARSE RESULT
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):
			if res.error: self.error = res.error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error
		return self

#######################################
# PARSER
#######################################
#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != TT_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	###################################

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register(self.advance())
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register(self.advance())
			return res.success(NumberNode(tok))

		elif tok.type == TT_LPAREN:
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN:
				res.register(self.advance())
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	###################################

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register(self.advance())
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)
#######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self
#######################################
# VALUES
#######################################

class Number:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Division by zero',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None

	def __repr__(self):
		return str(self.value)

#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]
class Interpreter:
	def visit(self, node, context):
		method_name = f'visit_{type(node).__name__}'
		method = getattr(self, method_name, self.no_visit_method)
		return method(node, context)

	def no_visit_method(self, node, context):
		raise Exception(f'No visit_{type(node).__name__} method defined')

	###################################

	def visit_NumberNode(self, node, context):
		return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)

	def visit_VarAccessNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = context.symbol_table.get(var_name)

		if not value:
			return res.failure(RTError(
				node.pos_start, node.pos_end,
				f"'{var_name}' is not defined",
				context
			))

		value = value.copy().set_pos(node.pos_start, node.pos_end)
		return res.success(value)

	def visit_VarAssignNode(self, node, context):
		res = RTResult()
		var_name = node.var_name_tok.value
		value = res.register(self.visit(node.value_node, context))
		if res.error: return res

		context.symbol_table.set(var_name, value)
		return res.success(value)

	def visit_BinOpNode(self, node, context):
		res = RTResult()
		left = res.register(self.visit(node.left_node, context))
		if res.error: return res
		right = res.register(self.visit(node.right_node, context))
		if res.error: return res

		if node.op_tok.type == TT_PLUS:
			result, error = left.added_to(right)
		elif node.op_tok.type == TT_MINUS:
			result, error = left.subbed_by(right)
		elif node.op_tok.type == TT_MUL:
			result, error = left.multed_by(right)
		elif node.op_tok.type == TT_DIV:
			result, error = left.dived_by(right)
		elif node.op_tok.type == TT_POW:
			result, error = left.powed_by(right)

		if error:
			return res.failure(error)
		else:
			return res.success(result.set_pos(node.pos_start, node.pos_end))

	def visit_UnaryOpNode(self, node, context):
		res = RTResult()
		number = res.register(self.visit(node.node, context))
		if res.error: return res

		error = None

		if node.op_tok.type == TT_MINUS:
			number, error = number.multed_by(Number(-1))

		if error:
			return res.failure(error)
		else:
			return res.success(number.set_pos(node.pos_start, node.pos_end))
#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.tokens = []  # List to store tokens
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    def make_word(self):
        word_str = ''

        while self.current_char is not None and WORD_REGEX.match(self.current_char):
            word_str += self.current_char
            self.advance()

        return Token(TT_WORD, word_str)
    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                spaces, tabs = 0, 0
                while self.current_char in ' \t':
                    if self.current_char == ' ':
                        spaces += 1
                    elif self.current_char == '\t':
                        tabs += 1
                    self.advance()
                if spaces > 0:
                    tokens.append(Token(TT_SPACE, spaces))
                if tabs > 0:
                    tokens.append(Token(TT_TAB, tabs))
            elif self.current_char == '\n':
                # Handle newlines to count lines
                lines = 0
                while self.current_char == '\n':
                    lines += 1
                    self.advance()
                tokens.append(Token(TT_LINE, lines))
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(TT_MOD))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == 'while':
                tokens.append(Token(TT_WHILE))
                self.advance()
            elif self.current_char == 'else':
                tokens.append(Token(TT_ELSE))
                self.advance()
            elif self.current_char == 'for':
                tokens.append(Token(TT_FOR))
                self.advance()
            elif self.current_char == 'function':
                tokens.append(Token(TT_FUNCTION))
                self.advance()
            elif self.current_char == 'static':
                tokens.append(Token(TT_STATIC))
                self.advance()    
            elif self.current_char == 'return':
                tokens.append(Token(TT_RETURN))
                self.advance()
            elif self.current_char == 'Public':
                tokens.append(Token(TT_PUBLIC))
                self.advance()
            elif self.current_char == 'Private':
                tokens.append(Token(TT_PRIVATE))
                self.advance()
            elif self.current_char == 'null':
                tokens.append(Token(TT_NULL))
                self.advance()  
            elif self.current_char == '\\':
                tokens.append(Token(TT_SINGLE_LINE_COMMENT))
                self.advance()  
            elif self.current_char == '\\*':
                tokens.append(Token(TT_MULTI_LINE_COMMENT))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMICOLON))
                self.advance()
            elif self.current_char == '>':
                tokens.append(Token(TT_GE))
                self.advance()
            elif self.current_char == '<':
                tokens.append(Token(TT_SM))
                self.advance()
            elif self.current_char == '&':
                tokens.append(Token(TT_BIT_AND))
                self.advance()
            elif self.current_char == '|':
                tokens.append(Token(TT_BIT_OR))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_BIT_XOR))
                self.advance()
            elif self.current_char == '~':
                tokens.append(Token(TT_BIT_NOT))
                self.advance()
            elif self.current_char == '<<':
                tokens.append(Token(TT_LSHIFT))
                self.advance()
            elif self.current_char == '>>':
                tokens.append(Token(TT_RSHIFT))
                self.advance()
            elif self.current_char == 'New':
                tokens.append(Token(TT_NEW))
                self.advance()
            elif self.current_char == 'Class':
                tokens.append(Token(TT_CLASS))
                self.advance()
            elif WORD_REGEX.match(self.current_char):  # Check if the current character is part of a word
                tokens.append(self.make_word())  # Tokenize words
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                tokens.append(Token('OTHER', char))
        self.tokens=tokens 
        # Add the logic to check if the last token is a number and if it's even or odd   
        if tokens and tokens[-1].type == TT_INT:
            number = int(tokens[-1].value)
            if number % 2 == 0:
                tokens.append(Token(TT_EVEN))
            else:
                tokens.append(Token(TT_ODD))    
        return self.tokens, None       

#######################################
# RUN
#######################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0))
global_symbol_table.set("FALSE", Number(0))
global_symbol_table.set("TRUE", Number(1))

def run(fn, text):
	# Generate tokens
	lexer = Lexer(fn, text)
	tokens, error = lexer.make_tokens()
	if error: return None, error
	
	# Generate AST
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error: return None, ast.error

	# Run program
	interpreter = Interpreter()
	context = Context('<program>')
	context.symbol_table = global_symbol_table
	result = interpreter.visit(ast.node, context)

	return result.value, result.error

###################### 
#######  Lex program to count the number of lines, spaces and tabs #####

def count_lines_spaces_tabs(text):
    lexer = Lexer("input.txt", text)
    tokens, error = lexer.make_tokens()

    if error:
        return str(error)

    line_count, space_count, tab_count = 0, 0, 0

    for token in tokens:
        if token.type == TT_LINE:
            line_count += token.value
        elif token.type == TT_SPACE:
            space_count += token.value
        elif token.type == TT_TAB:
            tab_count += token.value

    return f"Total lines: {line_count}, Total spaces: {space_count}, Total tabs: {tab_count}"

###################  
def count_tokens(self):
        return len(self.tokens)

# Bind the method to the class
Lexer.count_tokens = count_tokens

######################
def make_number(self):
    num_str = ''
    
    while self.current_char is not None and self.current_char in DIGITS:
        num_str += self.current_char
        self.advance()
    
    return Token(TT_DIGIT, num_str)

############ MAIN FUNCTION ##########

if __name__ == "__main__":
    input_text = "Hello Wrld nijofv  kdfngsnk  kbnngkn/n/nknnknlnkg"
    lexer = Lexer("input.txt", input_text)
    tokens, _ = lexer.make_tokens()
    total_tokens = lexer.count_tokens()  # Call the method on the lexer instance
    print(f"Total Tokens: {total_tokens}")
    result = count_lines_spaces_tabs(input_text)
    print(result)

    