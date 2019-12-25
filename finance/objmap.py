"""
A script to play with the personal capital api.
"""
import dataclasses
import inspect
import typing


# noinspection PyArgumentList
@dataclasses.dataclass()
class ObjectMapping:
    """
    A base class to aid in creating objects from JSON.
    """
    @classmethod
    def safe_init(cls, instance: typing.Any, **kwargs) -> 'ObjectMapping':
        """
        Create an object from the keyword arguments.
        Silently ignore any keyword arguments that are not known.
        """
        skwargs = {}
        for name in inspect.signature(cls).parameters:
            try:
                skwargs[name] = kwargs[name]
            except KeyError:
                try:
                    skwargs[name] = getattr(instance, name)
                except AttributeError:
                    pass

        return cls(**skwargs)

    def fillna(self, rules: typing.List[typing.MutableMapping]) -> 'ObjectMapping':
        """
        Fill in missing values based on the list of rules.

        The rules is a list of of `where` and `value` mappings.
        An update occurs when all instance variables match the `where` items.
        The items from the `values` mapping are used when the update step occurs.

        Parameters:
            rules: A list of rule mappings.

        Returns:
            The updated instance with missing values filled in based on the rules.
        """
        for i, rule in enumerate(rules):
            if self._matches(**rule['where']):
                self._update(**rule['value'])
                rules.pop(i)
                break

        return self

    def _matches(self, **kwargs) -> bool:
        """
        Check to see if key-value pair matches.

        Returns:
            True if all items match.
        """
        if not kwargs:
            return False

        for k, v in kwargs.items():
            if getattr(self, k) != v:
                return False

        return True

    def _update(self, **kwargs):
        """
        Update attributes using key-value pairs.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(k)
