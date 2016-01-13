import re
import os
import functools
import html
strictness = True
tokenising_expression = re.compile(r'(?:\{(?=%|\{))(.*?)(?:%|\})\}')
for_tokenising = re.compile(r'% for (.*) in (.*)')
if_tokenising = re.compile(r'% if (.*)')


class ParseError(Exception):
    def __init__(self, msg):
        return super().__init__(msg)


def html_escape(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        return html.escape(func(*args, **kwargs))
    return inner


class Node:
    def __init__(self, content, parent):
        self.content = content
        self.parent = parent

    def evaluate(self, context):
        raise NotImplementedError()


class TextNode(Node):
    def evaluate(self, context):
        return self.content


class PythonNode(Node):
    @html_escape
    def evaluate(self, context):
        try:
            return str(eval(self.content, {}, context))
        except NameError:
            if not strictness:
                return '{{}}'
            return str(eval(self.content, {}, context))


class SafePythonNode(Node):
    def evaluate(self, context):
        try:
            return str(eval(self.content, {}, context))
        except NameError:
            if not strictness:
                return '{{}}'
            return str(eval(self.content, {}, context))


class IncludeNode(Node):
    def evaluate(self, context):
        try:
            with open(self.content) as f:
                return render_template(f.read(), context)
        except FileNotFoundError:
            raise ParseError('\nIncluded file: {} is nonexistent'.format(self.content))


class ForNode(Node):
    """
    iterator: list of strings
    """
    def __init__(self, parent, iterator, iterable, child_group, empty_group):
        self.parent = parent
        self.iterator = iterator
        self.iterable = iterable
        self.child_group = child_group
        self.empty_group = empty_group

    def evaluate(self, context):
        iterable = eval(self.iterable, {}, context)
        if len(iterable) == 0 and self.empty_group is not None:
            return self.empty_group.evaluate(context)

        for_list = []
        for item in iterable:
            contextCopy = dict(context)
            if len(self.iterator) > 1:
                for var_name, var_value in zip(self.iterator, item):
                    contextCopy[var_name] = var_value
            else:
                contextCopy[self.iterator[0]] = item
            for_list.append(self.child_group.evaluate(contextCopy))
        return ''.join(str(i) for i in for_list)


class IfNode(Node):
    def __init__(self, parent, predicate, main_child, else_child):
        self.parent = parent
        self.predicate = predicate
        self.main_child = main_child
        self.else_child = else_child

    def evaluate(self, context):
        if eval(self.predicate, {}, context):
            return self.main_child.evaluate(context)
        else:
            if self.else_child is not None:
                return self.else_child.evaluate(context)
            return ''


class CommentNode(Node):
    def __init__(self, parent):
        self.parent = parent

    def evaluate(self, context):
        return ''


class LetNode(Node):
    def evaluate(self, context):
        exec(self.content, {}, context)
        return ''


class GroupNode(Node):
    def evaluate(self, context):
        group_list = []
        context = dict(context)
        for node in self.content:
            group_list.append(node.evaluate(context))
        return ''.join(str(i) for i in group_list)


def _notFinished(parent, lookingAt, template):
    if lookingAt >= len(template):
        return False
    lookingAt = template[lookingAt]
    if isinstance(parent, ForNode):
        if lookingAt == '% end for ':
            return False
        if lookingAt == '% empty ':
            return False
    if isinstance(parent, IfNode):
        if lookingAt == '% end if ':
            return False
        if lookingAt == '% else ':
            return False
    if isinstance(parent, CommentNode):
        if lookingAt == '% end comment ':
            return False
    return True


def _tokenise(template):
    return re.split(tokenising_expression, template)


def _parse_template(template, upto, parent):
    root_node = GroupNode([], parent)
    content = []
    index = upto
    while _notFinished(parent, index, template):
        token = template[index]
        offset = None
        if token.startswith('{'):
            token = PythonNode(token[1:].strip(), root_node)
        elif token.startswith('% safe '):
            token = SafePythonNode(token[len('% safe '):-1], root_node)
        elif token.startswith('% include'):
            token = IncludeNode(token[len('% include '):-1], root_node)
        elif token.startswith('% let '):
            token = LetNode(token[len('% let '): -1], root_node)
        elif token.startswith('% for'):
            for_token = re.match(for_tokenising, token)
            iterator, iterable = for_token.group(1).strip(), for_token.group(2).strip()
            iterator = [i.strip() for i in iterator.split(',')]
            token = ForNode(root_node, iterator, iterable, None, None)
            child_group, offset = _parse_template(template, index + 1, token)
            token.child_group = child_group
            if template[offset] == '% empty ':
                empty_group, offset = _parse_template(template, offset + 1, token)
                token.empty_group = empty_group
        elif token.startswith('% if'):
            if_token = re.match(if_tokenising, token)
            predicate = if_token.group(1).strip()
            token = IfNode(root_node, predicate, None, None)
            main_child, offset = _parse_template(template, index + 1, token)
            token.main_child = main_child
            if template[offset] == '% else ':
                else_child, offset = _parse_template(template, offset + 1, token)
                token.else_child = else_child
        elif token.startswith('% comment'):
            token = CommentNode(parent)
            _, offset = _parse_template(template, index + 1, token)
        else:
            token = TextNode(token, root_node)

        content.append(token)
        if offset is not None:
            index = offset
        index += 1
    root_node.content = content
    return (root_node, index)


def parse_template(template):
    tokenvalues = _tokenise(template)
    return _parse_template(tokenvalues, 0, None)


def render_template(template, context):
    return parse_template(template)[0].evaluate(context)


def render_file(filename, context, *, strict=False):  # TODO: strict=None
    global strictness
    # if strict is None:
    #     raise ParseError('Strictness must be specified')
    strictness = strict
    cur_directory = os.getcwd()
    try:
        with open(filename) as f:
            os.chdir(os.path.dirname(os.path.abspath(filename)))
            rendered = render_template(f.read(), context)
            return rendered

    except FileNotFoundError:
        raise ParseError('Tried to render nonexistent file - ' + filename)

    finally:
        os.chdir(cur_directory)
