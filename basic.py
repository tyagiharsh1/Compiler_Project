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

    