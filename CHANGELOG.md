# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Reverse rule default back to the equation of the original rule in case
  `NotImplementedError`
- `find_bijection_between` tries to find a bijection between classes given
  a `CombinatorialSpecificationSearcher` object for both.

### Fixed
- Removed a debug print
- Sharing of a specification html via gofile API.

### Deprecated
- Python 3.6 is no longer supported


## [3.0.0] - 2021-01-04
### Added
- Automatic bijection between equivalent specifications through the functions
  `get_bijection_to` and `are_isomorphic` of the specifications class. The bijection
  object holds a `map` function that performs the actual mapping.
- Sanity check for random sampling on rule
- Strategy must not define a `is_two_way` method in order to decide if they can
  be used to find the count of a children knowing the parent's and other
  children' count. If so the constructor returned by the new method
  `reverse_constructor` is used.
- Adds `expand_all_verified_with_pack` to `Specification` to attempt expansion of
  verified nodes with a given pack and time limit.
- Adds `unexpanded_verified_classes` to `Specification` to return the set of verified
  classes.

### Changed
- Specification are now built using a set of rules
- The json format of a spec is based storing the json format of its rule
- Streamlined the extraction of a specification from a searcher.
- All unary strategy are now store at the level of the equivalence database in
  order to avoid some productivity issue with catalytic variables.
- Adds a `max_expansion_time` optional parameter to
  `comb_spec_searcher._auto_search_rules`.

### Fixed
- `forward_map` of `EquivalencePathRule`
- `all_specifications` method of `RuleDB`

## [2.4.0] - 2020-11-11
### Changed
- Computation of terms in the constructor is now on a per size basis. The value for each possible parameters is computed at once in the new `get_terms` function of constructor. If you do not implement your own constructor this should have no effect on your code. The old `generate_object_of_size` method of the constructor is also replaced by a `get_objects` method that returns the objects for each possible combination of parameters.

## [2.3.0] - 2020-10-28
### Added
- Can sample and generate objects from specifications using multiple parameters.
- Sanity check tests object generation for rules with multiple parameteres.

### Changed
- Removed the processname extra from logging

## [2.2.1] - 2020-09-10
### Fixed
- when passed a multivariate function, the `taylor_expand` function expands in
  `x`.
- A division by zero error that occurred making the status update before
  starting to run.

## [2.2.0] - 2020-08-11
### Added
- using Github Actions for testing and deployment
- add specification sharing function to `ForestSpecificationDrawer`

### Changed
- when using a `LimitedStrategyRuleDB`, searching is aborted much faster when the root
  is not in the first pruned rules dictionary

### Fixed
- use `AbstractRule` instead of `Rule` in `_rules_from_strategy`
- fix `CombinatorialSpecification.share()` which was missing

## [2.1.1] - 2020-08-06
### Fixed
- fixed the type hints

## [2.1.0] - 2020-08-06
### Added
- a `SpecificationDrawer` for visualizing `CombinatorialSpecification`
- `show` method to `CombinatorialSpecification`
- `to_html_representation` method to `CombinatorialClass`
- `AbstractStrategy` raises `StrategyDoesNotApply` in the `__call__` method
- function `CombinatorialSpecification.share_spec()` which uploads the spec to a file
  sharing site
- more verbose logging during the specification creation process

### Changed
- Improved the status update
- `rule_from_equivalence_rule_dict` now takes a list of expected equivalence rules so a
  much smaller dictionary is produced

### Fixed
- fixed `ProofTree` handling of getting rules from spec
- fixed printing of `InvalidOperationError` message

## [2.0.0] - 2020-07-16
### Added
- the methods `expand_verified` and `expand_comb_class` on
  `CombinatorialSpecification`
- the `get_rule` method on `CombinatorialSpecification` can also take a label
  as a key
- `expand_verified` flag to the initialiser of
  `CombinatorialSpecificationSearcher` which will expand verified classes using
  the pack passed to the `CombinatorialSpecificationSearcher`
- `rule_from_equivalence_rule_dict` to `RuleDBBase`
- It is now possible to get all the combinatorial classes contained in a specification
  with the `comb_classes` method.

### Changed
- When expanding verified nodes in a specification, the search now uses
  `_auto_search_rules`, instead of `do_level` and `get_smallest_specification`.
  This is a stripped back auto search method returning the equivalence paths
  and strategies needed to create a specification.
- the `get_eq_symbol` and `get_op_symbol` are moved to `AbstractStrategy`
  rather than `Constructor`
- the `expand_verified` flag on the `auto_search` method and
  `CombinitorialSpecification.__init__` method was removed, and the
  default is now to not expand verified classes. You should use the
  `expand_verified` method on `CombinatorialSpecification` for the same
  behaviour.
  It also no longer logs the string of the specification.

### Fixed
- fixed sanity checking in `comb_spec_searcher`
- the initialiser of `CombinatorialSpecification` removes redundant rules

### Removed
- `DisableLogging` was removed from `utils` as it is no longer used.

## [1.3.0] - 2020-07-07
### Added
- added an optional `fixed_values` parameter to the `DisjointUnion` constructor,
  that allows you to set a value that a child's parameter must take.
- add the abstract method `can_be_equivalent` to `AbstractStrategy`.

### Changed
- removed the method `is_equivalence` from `Constructor`. You should instead
  use the `is_equivalence` method on the `Rule`.
- the `CartesianProduct` now considers compositions of all parameters and
  not just `n`.
- the `RelianceProfile` type changed to work multiple parameters. It is now a
  dictionary pointing from parameters to the values.

### Fixed
- ignore rules where the left and non-empty right hand sides are the same

## [1.2.0] - 2020-06-29
### Added
- Support for maple equations in multiple variables
- an option on `auto_search` to not expand verified classes
- a `LimitedStrategyRuleDB` to find specifications with no more than a given number of
  strategies of certain types
- log information when expanding a verified combinatorial class.
- added `is_equivalence` method to `Rule`
- sanity checking in multiple variables. In order to use this one must implement
  the method `possible_parameters` on their `CombinatorialClass`. The sanity
  checker only checks counts, not generation of objects.
- Added the `initial_conditions` method to `CombinatorialClass` and a
  `get_initial_conditions` method to `CombinatorialSpecification`.

### Fixed
- when subbing parameters use simultaneous flag
- Retrieving the rule in the forget db when the rules comes from applying a
  strategy to a child.
- When a parameter does not map to equivalent child we don't look for it on the
  child, preventing a `KeyError`.
- the extra parameters dictionary is flipped when creating the constructor in a
  reverse rule.
- fixed the `EquivalencePathRule.constructor` method
- only save equivalence rules for rules a -> (b,) if a and b are equivalent.

### Changed
- When the searcher finds a specification, it will now spends 1% of the time
  spent searching trying to find a small specification instead of just returning
  a random one.

## [1.1.0] - 2020-06-18
### Added
- When expanding a class with a strategy, you can now create rules where the
  parent is not the class passed to the strategy.
- The 'get_equations' method now handles multiple parameters


## [1.0.1] - 2020-06-17
### Changed
- Removed some of the detailed timing in the queue to make status report
  shorter.

## [1.0.0] - 2020-06-11
### Changed

This release is a major change of the `comb_spec_searcher` structure.
Instead of being centered around the `ProofTree` object, this version
introduces the `CombinatorialSpecification` object that offers many more
features. Most notably the support for arbitrary constructors, object building
and random sampling. The new version also widely improves support for multiple
variables.

## [0.5.0] - 2020-03-27
### Added
- `ProofTree.expand_tree()` is a method the can be used to expand a proof tree
  using a strategy pack. This can be used to expand strategy verified
  combinatorial classes, to give a single tree.

### Changed
- The `CombinatorialSpecification.auto_seach()` only uses keyword arguments.

### Fixed
- Fix the `is_expanded` function to check for inferral and initial expansion
- Fix the `__contain__` of ClassDB so that it actually works.

### Removed
- Support for Python 3.5 and earlier

## [0.4.0] - 2020-02-20
### Fixed
- Fix the dict method of Info so that it saves all the attributes.

### Changed
- If `forward_equivalence` is `False`, then if the constructor is one of
  `equiv`, `disjoint`, or `disjoint` the rule will be treated with forward
  equivalence.

## [0.3.0] - 2019-12-16
### Added
- `ProofTree.generate_objects_of_length()` implements an algorithm for
  generating the objects of a given length by utilising the structure implied
  by a proof tree.
- `ProofTreeNode.is_atom()` and `ProofTreeNode.is_epsilon()` methods for
  checking if a node represents an atom or epsilon.
### Changed
- Use polynomial algorithm for generating terms in random sampling code.

## [0.2.2] - 2019-09-06
### Added
- `ProofTree.count_objects_of_length()` implements the recurrence relation
  implied by the proof tree as long as the strategies used are only disjoint
  unions, decompositions, verification or recursion.

### Removed
- Remove the dependency on `permuta`.

## [0.2.1] - 2019-08-26
### Fixed
- Update sympy version to 1.4

## [0.2.0] - 2019-08-26
### Fixed
- Update the readme and test it
- Added missing equation for "F_root" case

## [0.1.0] - 2019-04-15
### Added
- This changelog file.
