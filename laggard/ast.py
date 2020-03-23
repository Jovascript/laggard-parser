import textwrap


class ASTNode:
    def __init__(self, children):
        self.children = children

    def __str__(self):
        return self.get_pretty_string()

    def __repr__(self):
        return "<{}>".format(self.get_name())

    def get_name(self):
        return self.__class__.__name__

    def get_children(self):
        return self.children

    def get_pretty_string(self, depth=-1):
        ret_str = self.get_name()
        if depth > 0 or depth == -1:
            if depth == -1:
                next_depth = -1
            else:
                next_depth = depth - 1
            children_str = ""
            for child in self.children:
                children_str += "\n"
                if isinstance(child, ASTNode):
                    children_str += child.get_pretty_string(depth=next_depth)
                else:
                    children_str += repr(child)
            ret_str += textwrap.indent(children_str, " " * 2)
        return ret_str
