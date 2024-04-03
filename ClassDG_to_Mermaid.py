import sys
from ply import lex, yacc

class ClassDG:

    def __init__(self):
        self.lexer = None
        self.parser = None

    # LEXER
    tokens = (
        # Fixed tokens
        'CLASS',
        'MINUS',
        'PLUS',
        'COMMA',
        'LPAREN',
        'RPAREN',
        'COLON',
        'LBRACE',
        'RBRACE',
        'INHERITANCE',
        'DEPENDENCY',
        'AGGREGATION',
        'COMPOSITION',
        'CARDINALITY',
        # Tokens with dynamic values
        'ID',
    )

    t_MINUS = r'-'
    t_PLUS = r'\+'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r'\,'
    t_COLON = r'\:'
    t_ignore = ' \t\n'

    def t_CLASS(self, t):
        r'class'
        return t

    def t_INHERITANCE(self, t):
        r'(->>|<<-)'
        t.value = "<|--" if t.value == "<<-" else "--|>"
        return t

    def t_DEPENDENCY(self, t):
        r'(->|<-)'
        t.value = "<.." if t.value == "<-" else "..>"
        return t

    def t_AGGREGATION(self, t):
        r'(<>->|<-<>)'
        t.value = "--o" if t.value == "<-<>" else "o--"
        return t

    def t_COMPOSITION(self, t):
        r'(<<>>->|<-<<>>)'
        t.value = "--*" if t.value == "<-<<>>" else "*--"
        return t

    def t_CARDINALITY(self, t):
        r'\'[0-9]+(\.\.\*)?\'|\'n(\.\.\*)?\''
        t.value = str(t.value.replace("\'","\""))
        return t

    def t_ID(self, t):
        r'[a-zA-Z0-9_]+'
        t.value = str(t.value)
        return t

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

    def build_lexer(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # PARSER

    def p_instruction(self, p):
        '''instruction : class instruction
                       | relationship instruction
                       | class
                       | relationship '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + '\n' + p[2]

    def p_class_definition(self, p):
        '''class : CLASS ID LBRACE class_body RBRACE'''
        p[0] = f"{p[1]} {p[2]} {p[3]}\n{p[4]}\n{p[5]}"

    def p_relationship(self, p):
        '''relationship : ID CARDINALITY relation CARDINALITY ID
                        | ID relation ID'''
        if len(p) == 4:
            p[0] = f"{p[1]} {p[2]} {p[3]}"
        else:
            p[0] = f"{p[1]} {p[2]} {p[3]} {p[4]} {p[5]}"

    def p_relation(self, p):
        '''relation : MINUS
                    | INHERITANCE
                    | DEPENDENCY
                    | AGGREGATION
                    | COMPOSITION'''
        if p[1] == "-":
            p[1] = "--"
        p[0] = p[1]

    def p_class_body(self, p):
        '''class_body : class_body class_member
                      | class_member'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + '\n' + p[2]

    def p_class_member(self, p):
        '''class_member : attribute
                        | method'''
        p[0] = '\t' + p[1]

    def p_attribute(self, p):
        '''attribute : access_modifier ID COLON ID'''
        p[0] = f"{p[1]}{p[4]} {p[2]}"

    def p_method(self, p):
        '''method : access_modifier ID LPAREN parameter RPAREN COLON ID'''
        p[0] = f"{p[1]}{p[2]}({p[4]}){p[6]} {p[7]}"

    def p_access_modifier(self, p):
        '''access_modifier : PLUS
                           | MINUS'''
        p[0] = p[1]

    def p_parameter(self, p):
        '''parameter : ID COLON ID COMMA parameter
                     | ID COLON ID
                     | empty'''
        if len(p) == 4:
            p[0] = f"{p[3]} {p[1]}"
        elif len(p) == 6:
            p[0] = f"{p[3]} {p[1]}{p[4]} {p[5]}"
        else:
            p[0] = p[1]

    def p_empty(self, p):
        '''empty :'''
        p[0] = ""

    def p_error(self, p):
        print("Syntax error in input!", p)

    def build_parser(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        return "classDiagram\n\n" + self.parser.parse(data)


if __name__ == "__main__":
    # Build the lexer and parser
    classDG = ClassDG()
    classDG.build_lexer()
    classDG.build_parser()

    # Get the input file content and pass throgh the parser
    if len(sys.argv) < 2:
        sys.exit("The input file in missing.")
    content = open(sys.argv[1]).read()

    # # To debug the lexer
    # classDG.lexer.input(content)
    # # Tokenize
    # while True:
    #     tok = classDG.lexer.token()
    #     if not tok:
    #         break  # No more input
    #     print(tok)

    # Execute the parser
    result = classDG.parse(content)
    print(result)

    # Save the result
    f = open("output.mermaid", "w")
    f.write(result)
    f.close()