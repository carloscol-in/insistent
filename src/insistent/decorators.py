import abc
import asyncio
import datetime
import time
from typing import Callable

from insistent import strategies as retry_strategies


class AbstractRetryDecorator(abc.ABC):
    _strategy: retry_strategies.AbstractRetryStrategy

    @abc.abstractmethod
    async def __call__(self):
        ...


class RetryDecorator():
    _strategy: retry_strategies.AbstractRetryStrategy

    def __init__(
        self,
        strategy: retry_strategies.AbstractRetryStrategy,
        logger: Callable,
    ):
        self._strategy = strategy
        self._logger = logger

    def __call__(self, func: Callable):
        """This will make the Retry instance a decorator
        by using Python's syntactic sugar for decorators.

        Args:
            func (Callable): The function you're decorating.
        """
        async def decorated(*args, **kwargs):
            count = 1
            start = datetime.datetime.now()
            for timeout in self._strategy():
                kwargs.update({'retry__try_count': count,
                              'retry__next_timeout': timeout})

                try:
                    self._logger(
                        f'Time elapsed before executing function {datetime.datetime.now() - start} seconds')
                    result = await func(*args, **kwargs)
                except (Exception, ValueError) as e:
                    # if timeout is None, then it was last run, return
                    if timeout is None:
                        return

                    self._logger(f'Exception was raised: {e}')
                    self._logger(
                        f'Decorated function tries count: #{count} | Retrying in {timeout} seconds | Continuing with Exception handlers.')
                    start = datetime.datetime.now()
                    # go to shhhleep... zzzz
                    await asyncio.sleep(timeout)
                    count += 1
                    # TODO: maybe execute some exception handlers here?
                    continue
                else:
                    self._logger(
                        'Decorated function returned a value successfully.')
                    return result

        return decorated


if __name__ == '__main__':
    def print_wrapper(prefix: str):
        def print_func(*args):
            print(prefix, *args)
        return print_func

    p_wrapper = print_wrapper('[RetryLogger]')

    retry = RetryDecorator(
        strategy=retry_strategies.ExponentialRetryStrategy(
            initial_timeout=1, retries=3, factor=2),
        logger=p_wrapper
    )

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
    result = say_hello('John', 'Jane')
    print(f'Result is {result}')
