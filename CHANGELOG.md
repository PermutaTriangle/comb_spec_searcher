# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support for maple equations in multiple variables
- an option on `auto_search` to not expand verified classes
- a `LimitedStrategyRuleDB` to find specifications with no more than a given number of
  strategies of certain types
- log information when expanding a verified combinatorial class.

### Fixed
- when subbing parameters use simultaneous flag
- Retrieving the rule in the forget db when the rules comes from applying a
  strategy to a child.

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
