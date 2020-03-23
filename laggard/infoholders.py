from collections import namedtuple

ParseInfo = namedtuple("ParseInfo", ["current_pos", "line_no", "col_no", "length", "section"])
TextPosition = namedtuple("Position", ["lineno", "columnno"])
