import re
from enum import Enum
from . import exceptions

OPEN_BLOCK_TAG = '{%'
CLOSE_BLOCK_TAG = '%}'
OPEN_VAR_TAG = '{{'
CLOSE_VAR_TAG = '}}'

tag_re = re.compile(r'(%s.*?%s|%s.*?%s)' % (
    re.escape(OPEN_BLOCK_TAG),
    re.escape(CLOSE_BLOCK_TAG),
    re.escape(OPEN_VAR_TAG),
    re.escape(CLOSE_VAR_TAG),
))


class TokenType(Enum):
    TEXT = 0
    VAR = 1
    BLOCK = 2


class Template:
    def __init__(self, template_string):
        lexer = Lexer(template_string)
        self.root = Parser(lexer).parse()

    def render(self, context={}):
        return self.root.render(context)


class Token:
    def __init__(self, token_type, contents):
        self.token_type = token_type
        self.contents = contents


class Lexer:
    def __init__(self, template_string):
        self.template_string = template_string

    def tokenize(self):
        for bit in tag_re.split(self.template_string):
            if bit:
                yield self.create_token(bit)

    def create_token(self, token_string):
        if not token_string.startswith(OPEN_BLOCK_TAG) and not token_string.startswith(OPEN_VAR_TAG):
            return Token(TokenType.TEXT, token_string)
        
        elif token_string.startswith(OPEN_VAR_TAG):
            return Token(TokenType.VAR, token_string[2:-2].strip())

        elif token_string.startswith(OPEN_BLOCK_TAG):
            return Token(TokenType.BLOCK, token_string[2:-2].strip())


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self):
        root = RootNode()
        scope_stack = [root]

        for token in self.lexer.tokenize():
            if not scope_stack:
                raise exceptions.TemplateError()

            parent_scope = scope_stack[-1]

            if token.contents in ('endif', 'endfor'):
                if token.contents != parent_scope.close_by:
                    raise exceptions.TemplateSyntaxError()

                scope_stack.pop()
                continue
            
            node = self.create_node(token)
            parent_scope.node_list.append(node)

            if isinstance(node, ElseNode):
                if hasattr(parent_scope, 'else_node') and parent_scope.else_node == -1:
                    parent_scope.else_node = len(parent_scope.node_list) - 1
                
                else:
                    raise exceptions.TemplateSyntaxError()

            if isinstance(node, ParentNode):
                scope_stack.append(node)
        
        if len(scope_stack) > 1:
            raise exceptions.TemplateSyntaxError()
        
        return root

    def create_node(self, token):
        if token.token_type == TokenType.TEXT:
            return TextNode(token.contents)

        elif token.token_type == TokenType.VAR:
            if not token.contents:
                raise exceptions.TemplateSyntaxError()

            return VarNode(token.contents)

        elif token.token_type == TokenType.BLOCK:
            command = token.contents.split()[0]

            if command == 'for':
                return ForNode(token.contents)

            elif command == 'if':
                return IfNode(token.contents)
            
            elif command == 'else':
                return ElseNode(token.contents)

            else:
                raise exceptions.TemplateSyntaxError()


def resolve(contents, context):
    for val in contents.split('.'):
        context = context.get(val)

        if context is None:
            raise exceptions.TemplateContextError()

    return context


class NodeList(list):
    def render(self, context):
        compiled_string = ''

        for node in self:
            compiled_string += node.render(context)
        
        return compiled_string


class Node():   
    def __init__(self, contents=None):
        self.contents = contents

    def render(self, context):
        pass


class ParentNode(Node):
    def __init__(self, contents=None):
        super().__init__(contents)
        self.node_list = NodeList()

    @property
    def close_by(self):
        pass

    def render(self, context):
        return self.node_list.render(context)


class TextNode(Node):
    def render(self, context):
        return self.contents


class VarNode(Node):
    def render(self, context):
        return str(resolve(self.contents, context))


class ElseNode(Node):
    pass


class RootNode(ParentNode):
    pass


class ForNode(ParentNode):
    @property
    def close_by(self):
        return 'endfor'

    def render(self, context):
        items = self.contents.split()[1:]
        compiled_string = ''
        
        if len(items) != 3:
            raise exceptions.TemplateSyntaxError()

        iter = resolve(items[2], context)

        for i in iter:
            inner_context = {**context, **{ items[0]: i }}
            compiled_string += self.node_list.render(inner_context)

        return compiled_string


class IfNode(ParentNode):
    def __init__(self, contents=None):
        super().__init__(contents)
        self.else_node = -1

    @property
    def close_by(self):
        return 'endif'

    def render(self, context):
        item = self.contents.split()[1:]

        if len(item) != 1:
            raise exceptions.TemplateSyntaxError()

        item = resolve(item[0], context)

        node_list = NodeList(self.node_list[self.else_node + 1:])

        if item:
            node_list = NodeList(self.node_list[:self.else_node])

        return node_list.render(context)