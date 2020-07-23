# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Improved the status update

### Fixed
- fixed `ProofTree` handling of getting rules from spec
- fixed printing of InvalidOperationError message

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
