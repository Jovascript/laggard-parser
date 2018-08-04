from copy import copy
from functools import wraps
from typing import List, Callable, Any, Union

from laggard.buffer import Buffer
from laggard.exceptions import ParseException, MalformedParserException


class RuleBuilder:
    """
    Builds rules, can be named(defined by user) or anonymous(part of generation annoyances, will get flattened
    in optimisation stage).

    This class is the base class for all of the parsers.

    Examples:
        Many magic methods are implemented.

        Bitwise OR will produce a :class:`~laggard.rulebuilders.Choice`::

            rulebuilder | rulebuilder

        Bitwise AND will prodice a :class:`~laggard.rulebuilders.Combined`::

            rulebuilder & rulebuilder

        Calling a rulebuilder will add an alias, which can be referenced in transformers for :class:`~laggard.rulebuilders.Combined` rules::

            rulebuilder("myalias")

    Warnings:
        Do not initialise directly, but use the factory function :staticmethod:`~laggard.rulebuilders.RuleBuilder.create`
    """

    @staticmethod
    def create(source, **kwargs):
        """
        The factory method for all RuleBuilders.
        This function decides on the type of `source`.

        * If source is a RuleBuilder it will be reconfigured with the provided `kwargs`.
        * If source is a RulePlaceholder, it will be invoked.
        * If source is callable, a :class:`~laggard.functionalrulebuilders.FunctionalRuleBuilder` will be returned.
        * If source is a string, the string will be expected(:class:`~laggard.functionalrulebuilders.LiteralExpecter`)
        * If source is a iterable(list etc.), it will be considered a charset match(:class:`~laggard.functionalrulebuilders.CharsetExpecter`)


        Args:
            source (Union[RuleBuilder, RulePlaceholder, Callable, str, list]: The object the RuleBuilder is created from
            **kwargs: Miscellaneous options

        Keyword Args:
            multiple(bool): If True, the rule will *require* 1 or more matches
            optional(bool): If True, the rule will return `None` if it fails to parse.
                If both `multiple` and `optional` are True, the rule will behave like the regex * operator.
            name(str): If specified, the rule will be named(and not be anonymous)
            transformer(Callable): This will recieve the parse result, and should return a modified parse result(good for making ASTs)


        Returns:
            RuleBuilder: Specific subclass depending on type given

        """
        # These things call this function
        from laggard.helpers import RulePlaceholder
        from laggard.functionalrulebuilders import LiteralExpecter, CharsetExpecter, SomeOrNoneRule, MultipleRule, OptionalRule, FunctionalRuleBuilder
        if kwargs.pop("multiple", False):
            if kwargs.pop("optional", False):
                return SomeOrNoneRule(RuleBuilder.create(source), **kwargs)
            else:
                return MultipleRule(RuleBuilder.create(source), **kwargs)
        elif kwargs.get("optional", False):
            return OptionalRule(RuleBuilder.create(source), **kwargs)
        else:
            if isinstance(source, RuleBuilder):
                source.reconfigure(**kwargs)
                return source
            elif isinstance(source, RulePlaceholder):
                return source.invoke(**kwargs)
            elif callable(source):
                return FunctionalRuleBuilder(source, **kwargs)
            elif isinstance(source, str):
                return LiteralExpecter(source, **kwargs)
            elif isinstance(source, (list, set, tuple)):
                return CharsetExpecter(source, **kwargs)
            else:
                raise MalformedParserException("Cannot create RuleBuilder from object of type '{}'".format(type(source).__name__))

    def __init__(self, **kwargs):
        self.name: str = None
        self.transformer: Callable = None

        self.reconfigure(**kwargs)

        self.alias = None

    def reconfigure(self, **kwargs):
        """
        Change certain fields, and custom attributes, without creating a whole new class.

        Args:
            **kwargs: Any parameters to change, like the constructor.
        """
        self.name = kwargs.get("name", self.name)
        self.transformer = kwargs.get("transformer", self.transformer)

    @property
    def anonymous(self):
        """
        bool: Whether the RuleBuilder has a name or alias; can it be removed without damaging the defined structure?
        """
        return self.name is None and self.alias is None

    def __or__(self, other):
        if isinstance(other, RuleBuilder):
            return Choice(self, other)
        else:
            return Choice(self, RuleBuilder.create(other))

    def __ror__(self, other):
        return Choice(RuleBuilder.create(other), self)

    def __and__(self, other):
        if isinstance(other, RuleBuilder):
            return Combined(self, other)
        else:
            return Combined(self, RuleBuilder.create(other))

    def __rand__(self, other):
        return Choice(RuleBuilder.create(other), self)

    def __call__(self, alias):
        """Allows a rule to be labelled locally"""
        x = copy(self)
        x.alias = alias
        return x

    def flatten(self):
        """
        Modifies the RuleBuilder, and its children, to form a more efficient structure.

        Notes:
            This is automatically called by :meth:`~laggard.rulebuilders.RuleBuilder.generate_complete_parser`.
        """
        pass

    def generate_parser(self) -> Callable[[Buffer], Any]:
        """
        Creates the function which receives the buffer, and returns the *raw* parsing result.

        Returns:
            A parser function of signature (:class:`~laggard.buffer.Buffer') -> Any
        """
        pass

    def generate_complete_parser(self) -> Callable[[Buffer], Any]:
        """
        Creates the function which receives the buffer, and returns the *processed* parsing result(if user specified a transformation).

        Returns:
            A parser function, but which also calls the transformer.
        """
        self.flatten()
        parse = self.generate_parser()
        if self.transformer is not None:
            transform = self.transformer

            @wraps(parse)
            def wrapper(buffer: Buffer):
                result = parse(buffer)
                return transform(result)

            return wrapper
        else:
            @wraps(parse)
            def wrapper(buffer: Buffer):
                return parse(buffer)

            return wrapper


class Choice(RuleBuilder):
    """
    Defines a rule which requires one of many subrules to be matched.

    Each subrule is attempted in the order they were specified.
    If all fail to parse, the whole rule will fail.
    """

    def __init__(self, *args):
        super().__init__()
        self._choices: List[RuleBuilder] = list(args)

    @property
    def choices(self):
        return self._choices

    def flatten(self):
        for i, rule in enumerate(self._choices):
            rule.flatten()
            if isinstance(rule, Choice) and rule.anonymous:
                rule: Choice
                self._choices[i: i + 1] = rule.choices

    def generate_parser(self):
        parsers = [rule.generate_complete_parser() for rule in self._choices]

        def _(buffer: Buffer):
            with buffer:
                for i, parser in enumerate(parsers):
                    try:
                        return parser(buffer)
                    except ParseException:
                        if (i + 1) == len(parsers):
                            raise

        return _


class Combined(RuleBuilder):
    """
    Defines a rule which requires the sequential matching of several subrules.

    If any one of the specified subrules fail to parse, the whole rule will parse.
    The parser will return a :class:`~laggard.helpers.OptionallyNamedTuple`, with names if any of the subrules had an alias.
    """

    def __init__(self, *args):
        super().__init__()
        self._combined = list(args)

    @property
    def combined(self):
        return self._combined

    def flatten(self):
        for i, rule in enumerate(self._combined):
            rule.flatten()
            if isinstance(rule, Combined) and rule.anonymous:
                rule: Combined
                self._combined[i: i + 1] = rule.combined

    def generate_parser(self):
        parsers = [rule.generate_complete_parser() for rule in self._combined]
        from laggard.helpers import OptionallyNamedTuple
        result_formatter = OptionallyNamedTuple.create(list(map(lambda x: x.alias, self._combined)))

        def _(buffer: Buffer):
            with buffer:
                results = list(map(lambda x: x(buffer), parsers))
                return result_formatter(results)

        return _
