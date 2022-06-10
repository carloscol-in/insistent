import abc
import asyncio
from typing import Callable

from insistent import decorators as retry_decorators
from insistent import strategies as retry_strategies


class AbstractRetryDecoratorBuilder(abc.ABC):
    _timeout: int
    _retries: int
    _strategy: retry_strategies.AbstractRetryStrategy
    _logger: Callable

    @abc.abstractmethod
    def build(self) -> retry_decorators.AbstractRetryDecorator:
        """Build the RetryDecorator object with the passed parameters, or
        default in the case of the necessary.
        """
        ...

    @abc.abstractmethod
    def set_initial_timeout(self, timeout: int) -> 'AbstractRetryDecoratorBuilder':
        """Use this extension method to set the initial timeout for the retry code.

        Args:
            timeout (int): Time in seconds, which determines the initial
            timeout interval used for retry logic.

        Returns:
            AbstractRetryDecoratorBuilder: This builder object.
        """
        ...

    @abc.abstractmethod
    def set_retries(self, retries: int) -> 'AbstractRetryDecoratorBuilder':
        """Use this extension method to set the amount of times the code
        should be retried.

        Args:
            retries (int): Amount of retries.

        Returns:
            AbstractRetryDecoratorBuilder: This builder object.
        """
        ...

    @abc.abstractmethod
    def set_strategy(self, strategy_class: retry_strategies.AbstractRetryStrategy, *args, **kwargs) -> 'AbstractRetryDecoratorBuilder':
        ...

    @abc.abstractmethod
    def set_logger(self, logger: Callable) -> 'AbstractRetryDecoratorBuilder':
        ...


class RetryDecoratorBuilder(AbstractRetryDecoratorBuilder):
    _timeout: int
    _retries: int
    _strategy: retry_strategies.AbstractRetryStrategy

    def build(self) -> retry_decorators.AbstractRetryDecorator:
        decorator = retry_decorators.RetryDecorator(
            strategy=self._strategy,
            logger=self._logger
        )
        return decorator

    def set_initial_timeout(self, timeout: int) -> 'AbstractRetryDecoratorBuilder':
        if timeout <= 0:
            raise ValueError("Timeout has to be bigger than 0")
        self._timeout = timeout
        return self

    def set_retries(self, retries: int) -> 'AbstractRetryDecoratorBuilder':
        if retries <= 0:
            raise ValueError("Retries count has to be bigger than 0")
        self._retries = retries
        return self

    def set_strategy(self, strategy_class: retry_strategies.AbstractRetryStrategy, *args, **kwargs) -> 'AbstractRetryDecoratorBuilder':
        self._strategy = strategy_class(
            self._timeout,
            self._retries,
            *args,
            **kwargs
        )

        return self

    def set_logger(self, logger: Callable = None) -> 'AbstractRetryDecoratorBuilder':
        self._logger = logger if logger else print
        return self


if __name__ == '__main__':
    def print_wrapper(prefix: str):
        def print_func(*args):
            print(prefix, *args)
        return print_func

    p_wrapper = print_wrapper('[RetryLogger]')

    retry = RetryDecoratorBuilder()\
        .set_initial_timeout(1)\
        .set_retries(3)\
        .set_logger(p_wrapper)\
        .set_strategy(retry_strategies.ExponentialRetryStrategy, factor=2)\
        .build()

    @retry
    def say_hello(to_user: str, from_user: str, retry__try_count: int, retry__next_timeout: int):
        print(f'-- {from_user} says hello to {to_user}')
        # code should be tried (n_retries + 1) times
        print(
            f'-- Code has been tried {retry__try_count} times. Next timeout of {retry__next_timeout} seconds.')

        # if retry__try_count > 2:
        #     return 123

        raise ValueError("I want to raise an exception because yes.")

    # call function without worrying of implementing retry correctly.
    result = asyncio.run(say_hello('John', 'Jane'))
    print(f'Result is {result}')
