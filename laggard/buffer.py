from laggard.exceptions import ParseException


class Buffer:
    def __init__(self, source: str, skip=[]):
        self.source = source
        self.stack = []
        self.current_index = 0
        self.skip = skip

    @property
    def last_pos(self) -> tuple:
        curi = self.stack[-1]
        lineno = self.source.count("\n", 0, curi)
        colno = self.current_index - self.source.rfind("\n", 0, curi)
        return (lineno, colno)

    @property
    def current_pos(self) -> tuple:
        lineno = self.source.count("\n", 0, self.current_index)
        colno = self.current_index - self.source.rfind("\n", 0, self.current_index)
        return (lineno, colno)

    def fetch(self, count: int = 1) -> str:
        retval = ""
        while len(retval) < count and self.current_index < len(self.source):
            if self.source[self.current_index] not in self.skip:
                retval += self.source[self.current_index]
            self.current_index += 1
        return retval

    def mark(self):
        self.stack.append(self.current_index)
        print(len(self.stack))

    def abandon(self):
        self.current_index = self.stack.pop()

    def commit(self):
        self.stack.pop()

    def cry(self, message):
        raise ParseException("Failed to parse: {} at {}".format(message, self.last_pos))

    def __enter__(self):
        self.mark()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.abandon()
        else:
            self.commit()
