from Strategies.BuyLowSellHigh import BuyLowSellHigh


class StrategySelector:
    strategies = {
        "BuyLowSellHigh": BuyLowSellHigh,
    }

    static_strategy_keys = [
        "random",
        #    "rsi",
        #    "hold",
        "scalping"
    ]

    def select(self, strategy_code, **args):
        return self.strategies[strategy_code](**args)

    def get_all_strategies(self, only_static=False):
        if only_static:
            return self.static_strategy_keys
        return self.strategies.keys()
