from PyQt6 import QtCore, QtGui


class MineScriptHighlighter(QtGui.QSyntaxHighlighter):
    def create_format(foreground_color: QtGui.QColor):
        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(foreground_color)
        return keyword_format

    operators = (r"\+", "-", r"\*", "=", "<>", "<", "<=", ">", ">=")
    bool_operators = ("and", "or", "not")
    literals = ("true", "false")
    numbers = (r"\d",)
    procedures = ("step forward", "turn by", "mine here", "print", "isThere")
    control_flow = ("if", "else", "while", "set", "to")
    all_keywords = (
        operators + bool_operators + literals + numbers + procedures + control_flow
    )

    operator_style = create_format(QtGui.QColor("#ff80ff"))
    bool_operator_style = create_format(QtGui.QColor("#df77ff"))
    literal_style = create_format(QtGui.QColor("#d6c2ff"))
    number_style = create_format(QtGui.QColor("#9d74ff"))
    procedure_style = create_format(QtGui.QColor("#4c97ff"))
    control_flow_style = create_format(QtGui.QColor("#ffab19"))
    variable_style = create_format(QtGui.QColor("#ff687c"))

    def __init__(self, parent):
        super().__init__(parent)

        self.highlighting_rules: list[
            tuple[QtCore.QRegularExpression, QtGui.QTextCharFormat]
        ] = []

        for words, style in (
            (self.operators, self.operator_style),
            (self.bool_operators, self.bool_operator_style),
            (self.literals, self.literal_style),
            (self.numbers, self.number_style),
            (self.procedures, self.procedure_style),
            (self.control_flow, self.control_flow_style),
        ):
            for word in words:
                pattern = QtCore.QRegularExpression(r"\b" + word + r"\b")
                self.highlighting_rules.append((pattern, style))

    def highlightBlock(self, text):
        self.setFormat(0, self.document().characterCount(), self.variable_style)

        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)

            while match_iterator.hasNext():
                match = match_iterator.next()

                start, length = match.capturedStart(), match.capturedLength()

                self.setFormat(start, length, format)


# a = 1 + 2 - 3 * 4
# 3 > a < 8
# 2 <= a >= 1

# True and not 7 or 1 < 45 + 2

# True, False

# 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

# print()
# next()

# if True:
#     pass
# else:
#     pass
# while False:
#     pass
