class YourDisjointStrategy(DisjointUnionStrategy):
    def decomposition_function(
        self, comb_class: CombinatorialClassType
    ) -> Optional[Tuple[CombinatorialClassType, ...]]:
        """
        Return the children of the strategy for the given comb_class. It
        should return None if it does not apply.
        """

    def formal_step(self) -> str:
        """
        Return a short string to explain what the strategy has done.
        """

    @classmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        return YourDisjointStrategy(
            ignore_parent=d.pop("ignore_parent"),
            inferrable=d.pop("inferrable"),
            possibly_empty=d.pop("possibly_empty"),
            workable=d.pop("workable"),
        )

    def forward_map(
        self,
        comb_class: CombinatorialClassType,
        obj: CombinatorialObjectType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    def __str__(self) -> str:
        pass


class YourCartesianProductStrategy(CartesianProductStrategy):
    def decomposition_function(
        self, comb_class: CombinatorialClassType
    ) -> Optional[Tuple[CombinatorialClassType, ...]]:
        """
        Return the children of the strategy for the given comb_class. It
        should return None if it does not apply.
        """

    def formal_step(self) -> str:
        """
        Return a short string to explain what the strategy has done.
        """

    @classmethod
    def from_dict(cls, d: dict) -> CSSstrategy:
        return YourCartesianProductStrategy(
            ignore_parent=d.pop("ignore_parent"),
            inferrable=d.pop("inferrable"),
            possibly_empty=d.pop("possibly_empty"),
            workable=d.pop("workable"),
        )

    def forward_map(
        self,
        comb_class: CombinatorialClassType,
        obj: CombinatorialObjectType,
        children: Optional[Tuple[CombinatorialClassType, ...]] = None,
    ) -> Tuple[Optional[CombinatorialObjectType], ...]:
        """
        The forward direction of the underlying bijection used for object
        generation and sampling.
        """
        if children is None:
            children = self.decomposition_function(comb_class)

    def __str__(self) -> str:
        pass


class YourStrategyFactory(StrategyFactory):
    def __call__(
        self, comb_class: CombinatorialClassType, **kwargs
    ) -> Iterator[Union[AbstractRule, AbstractStrategy]]:
        """
        Returns the results of the strategy on a comb_class.
        """

    def from_dict(cls, d: dict) -> CSSstrategy:
        return YourStrategyFactory(
            ignore_parent=d.pop("ignore_parent"),
            inferrable=d.pop("inferrable"),
            possibly_empty=d.pop("possibly_empty"),
            workable=d.pop("workable"),
        )

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass