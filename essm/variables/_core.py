# -*- coding: utf-8 -*-
"""Core variable type."""

from __future__ import absolute_import

import warnings

from sage.all import SR, Expression, var

from .units import SHORT_UNIT_SYMBOLS


class BaseVariable(Expression):
    """Physical variable."""

    @property
    def __doc__(self):
        return self.definition.__doc__

    @property
    def definition(self):
        return Variable.__registry__[self]

    @property
    def unit(self):
        return Variable.__units__[self]

    @property
    def short_unit(self):
        """Return short unit."""
        return (self * self.unit / self).subs(SHORT_UNIT_SYMBOLS)


class VariableMeta(type):
    """Variable interface.

    1. register domain (default: real)
    2. store _latex_() name
    3. register default values for each variable
    """

    def __new__(cls, name, parents, dct):
        """Build and register new variable."""
        if '__registry__' not in dct:
            name = dct.get('name', name)
            domain = dct.get('domain', 'real')
            unit = dct.get('unit', 1 / 1)
            latex_name = dct.get('latex_name')
            expr = BaseVariable(
                SR, SR.var(name, domain=domain, latex_name=latex_name))
            dct.update({
                'domain': domain,
                'expr': expr,
                'latex': expr._latex_(),
                'name': name,
                'unit': unit, })
            instance = super(VariableMeta, cls).__new__(
                cls, name, parents, dct)
            if expr in instance.__registry__:
                warnings.warn(
                    'Variable "{0}" will be overridden by "{1}"'.format(
                        instance.__registry__[expr].__module__ + ':' + name,
                        instance.__module__ + ':' + name, ),
                    stacklevel=2)
            instance.__registry__[expr] = instance
            if 'default' in dct:
                instance.__defaults__[expr] = dct['default']
            # Store unit for each variable:
            instance.__units__[expr] = unit
            return expr

        return super(VariableMeta, cls).__new__(cls, name, parents, dct)

    def __remove__(cls, expr):
        """Unregister a variable."""
        if expr in cls.__registry__:
            warnings.warn(
                'Variable "{0}" will be unregistered.'.format(
                    cls.__registry__[expr].__module__),
                stacklevel=2)
            del cls.__registry__[expr]
            del cls.__units__[expr]
            if expr in cls.__defaults__:
                del cls.__defaults__[expr]
        else:
            warnings.warn(
                'Variable "{0}" did not exist in registry.'.format(expr),
                stacklevel=2)


class Variable(object):
    """Base type for all physical variables."""
    __metaclass__ = VariableMeta
    __registry__ = {}
    __defaults__ = {}
    __units__ = {}


__all__ = ('Variable')
