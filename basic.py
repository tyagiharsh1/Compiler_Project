#######################################
# CONSTANTS
#######################################
import re
import fractions
WORD_REGEX = re.compile(r'[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*')
# EMAIL_REGEX for checking valid email addresses
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
##  regular expression pattern for valid mobile numbers.
MOBILE_REGEX = re.compile(r'^\d{10}$')
FRACTION_REGEX = re.compile(r'-?\d+/\d+')
EVEN_A_REGEX = re.compile(r'^[b]*((a[ab]*){2})*$')
ENDS_WITH_11_REGEX = re.compile(r'^.*11$')
ODD_ZEROS_EVEN_ONES_REGEX = re.compile(r'^(00*1(11)*0)*1*$')
########## Regular expression for identifier
IDENTIFIER_REGEX = re.compile(r'^[a-zA-Z_]\w*$')
DATE_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')


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
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
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


################# 
### function to count the number of words in a string  ###

def count_words(text):
    lexer = Lexer("input.txt", text)
    tokens, error = lexer.make_tokens()

    if error:
        return str(error)

    word_count = 0
    for token in tokens:
        if token.type == TT_WORD:
            word_count += 1

    return f"Total words: {word_count}"


###################  
def count_tokens(self):
        return len(self.tokens)

# Bind the method to the class
Lexer.count_tokens = count_tokens

########### Lex program to check whether given number is armstrong number or not
def is_armstrong_number(number):
    num_str = str(number)
    order = len(num_str)
    total = 0
    for digit in num_str:
        total += int(digit) ** order
    return total == number

# Function to check if a string is a valid email address
def is_valid_email(email):
    return EMAIL_REGEX.match(email) is not None

###
def is_valid_mobile_number(number):
    return MOBILE_REGEX.match(number) is not None   

#####

#### To check whether a number is prime or not in Python, you can add the following function to the code:

def is_prime(number):
    if number <= 1:
        return False
    if number <= 3:
        return True

    if number % 2 == 0 or number % 3 == 0:
        return False

    i = 5
    while i * i <= number:
        if number % i == 0 or number % (i + 2) == 0:
            return False
        i += 6

    return True

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
#################  Lex program to Count the Positive numbers, Negative numbers and Fractions
def count_numbers(numbers):
    positive_count = 0
    negative_count = 0
    fraction_count = 0

    for number in numbers:
        if number > 0:
            positive_count += 1
        elif number < 0:
            negative_count += 1
        elif isinstance(number, str) and FRACTION_REGEX.match(number):
            fraction_count += 1

    return positive_count, negative_count, fraction_count

#########################  Lex program to check perfect numbers  ###########


def is_perfect_number(number):
    if number <= 1:
        return False

    # Find divisors and sum them
    divisors_sum = 1  # 1 is always a divisor
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            divisors_sum += i
            if i != number // i:  # Avoid counting the same divisor twice for perfect squares
                divisors_sum += number // i

    return divisors_sum == number


##############
def count_vowels_consonants(text):
    vowels = "AEIOUaeiou"
    consonants = "BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz"

    vowel_count = 0
    consonant_count = 0

    for char in text:
        if char in vowels:
            vowel_count += 1
        elif char in consonants:
            consonant_count += 1

    return f"Vowels: {vowel_count}, Consonants: {consonant_count}"

###################

def starts_with_vowel(input_string):
    # Remove leading and trailing spaces from the input string
    input_string = input_string.strip()

    if len(input_string) == 0:
        return False  # Empty string is not considered to start with a vowel

    first_character = input_string[0].lower()

    # Check if the first character is a vowel (a, e, i, o, or u)
    if first_character in 'aeiou':
        return True
    else:
        return False
    
##############
def contains_non_alphabet_character(input_string):
    for char in input_string:
        if not char.isalpha():  # Check if the character is not an alphabet
            return True  # A non-alphabet character is found
    return False

########
def is_even_a_string(input_string):
    return bool(EVEN_A_REGEX.match(input_string))

###########
def is_ends_with_11(input_string):
    return bool(ENDS_WITH_11_REGEX.match(input_string))

########
def is_odd_zeros_even_ones(input_string):
    return bool(ODD_ZEROS_EVEN_ONES_REGEX.match(input_string))

################ Function to count words that are less than 10 and greater than 5 characters long
def count_words_between_5_and_10(text):
    # Use regular expression to find words
    words = re.findall(r'\b\w{6,9}\b', text)

    # Count the filtered words
    count = len(words)

    return count

#############################
def is_valid_identifier(identifier):
    return bool(IDENTIFIER_REGEX.match(identifier))

#####################
def is_leap_year(year):
    # A leap year is either divisible by 4 but not by 100, or divisible by 400.
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False
    
###################
def make_date(self):
        date_str = ''
        while self.current_char is not None and DATE_REGEX.match(self.current_char):
            date_str += self.current_char
            self.advance()
        return Token(TT_DATE, date_str)

######################
def make_number(self):
    num_str = ''
    
    while self.current_char is not None and self.current_char in DIGITS:
        num_str += self.current_char
        self.advance()
    
    return Token(TT_DIGIT, num_str)

############ MAIN FUNCTION ##########

if __name__ == "__main__":
    input_text = "hello world  Upes aaa nnn  kjnn\nThis is a test with spaces and tabs:\n\tTab1\n\t\tTab2\n   Space1\n Space2"
    lexer = Lexer("input.txt", input_text)
    tokens, _ = lexer.make_tokens()
    total_tokens = lexer.count_tokens()  # Call the method on the lexer instance
    print(f"Total Tokens: {total_tokens}")
    result = count_words(input_text)
    print(result)
    result = count_lines_spaces_tabs(input_text)
    print(result)

    number = 113  # Replace with your number
    if is_armstrong_number(number):
        print(f"{number} is an Armstrong number")
    else:
        print(f"{number} is not an Armstrong number")
    email = "csetanmayjain@gmail.com"  # Replace with the email address you want to check
    if is_valid_email(email):
        print(f"{email} is a valid email address")
    else:
        print(f"{email} is not a valid email address")

    mobile_number = "001112223"  # Replace with the mobile number you want to check
    if is_valid_mobile_number(mobile_number):
        print(f"{mobile_number} is a valid mobile number")
    else:
        print(f"{mobile_number} is not a valid mobile number")
    # Check if the number is prime
    if is_prime(number):
        print(f"{number} is a prime number")
    else:
        print(f"{number} is not a prime number")  

# Check if a string is a palindrome
    string_to_check = "Harsh"  # Replace with the string you want to check
    if is_palindrome(string_to_check):
        print(f'"{string_to_check}" is a palindrome')
    else:
        print(f'"{string_to_check}" is not a palindrome')  

numbers = [1, -2, 3.5, -0.5, 4, -5,3/2]
positive, negative, fractions = count_numbers(numbers)

print(f"Positive numbers: {positive}")
print(f"Negative numbers: {negative}")
print(f"Fractions: {fractions}")

number = 33
if is_perfect_number(number):
    print(f"{number} is a perfect number")
else:
    print(f"{number} is not a perfect number")

input_text = "Hello, World!"
result = count_vowels_consonants(input_text)
print(result)

###########
user_input = input("Enter a string: ")

if starts_with_vowel(user_input):
    print("The input string starts with a vowel.")
else:
    print("The input string does not start with a vowel.")
###
user_input = input("Enter a string: ")

if contains_non_alphabet_character(user_input):
    print("The input string contains non-alphabet characters.")
else:
    print("The input string consists of alphabets only.")

sample_text = "This is a sample text with words of various lengths. Some words are long, and some are short."

# Call the function with the sample text
result = count_words_between_5_and_10(sample_text)
print(f"Words between 6 and 9 characters long: {result}")
#############3

identifiers = ["my_variable", "My_Variable", "_private", "123variable", "not valid!"]

for identifier in identifiers:
    if is_valid_identifier(identifier):
        print(f"'{identifier}' is a valid Python identifier.")
    else:
        print(f"'{identifier}' is not a valid Python identifier.")
##################

year = int(input("Enter a year: "))

if is_leap_year(year):
    print(f"{year} is a leap year.")
else:
    print(f"{year} is not a leap year.")

if tokens and tokens[-1].type == TT_INT:
        number = int(tokens[-1].value)
        if number % 2 == 0:
            print(f"The last number {number} is even.")
        else:
            print(f"The last number {number} is odd.")

number_token = Token(TT_DIGIT, '1231')
if number_token.type == TT_DIGIT:
    print(f"{number_token.value} is a digit")
else:
    print(f"{number_token.value} is not a digit")

while True:
        input_string = input("Enter a string over the alphabet {a, b}, or type 'q' to quit: ")
        
        if input_string.lower() == 'q':
            print("Exiting the program.")
            break  # Exit the loop if 'q' is entered
        elif is_even_a_string(input_string):
            print("Accepted: The input string has an even number of 'a's.")
        else:
            print("Rejected: The input string does not have an even number of 'a's.")
        
        input_string = input("Enter a string or type 'q' to quit: ")
        
        if input_string.lower() == 'q':
            print("Exiting the program.")
            break  # Exit the loop if 'q' is entered
        elif is_ends_with_11(input_string):
            print("Accepted: The input string ends with '11'.")
        else:
            print("Rejected: The input string does not end with '11'.")
        input_string = input("Enter a string or type 'q' to quit: ")
        
        if input_string.lower() == 'q':
            print("Exiting the program.")
            break  # Exit the loop if 'q' is entered
        elif is_odd_zeros_even_ones(input_string):
            print("Accepted: The input string has an odd number of 0's and an even number of 1's.")
        else:
            print("Rejected: The input string does not meet the specified pattern.")

 