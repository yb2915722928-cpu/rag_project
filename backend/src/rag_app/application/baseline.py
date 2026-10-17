from collections.abc import Callable
from typing import Protocol

from rag_app.application.uow import TransactionSession, UnitOfWork


class BaselineReader(Protocol):
    def check(self) -> None: ...


def check_baseline(
    uow: UnitOfWork, repository: Callable[[TransactionSession], BaselineReader],
) -> None:
    with uow.transaction() as session:
        repository(session).check()
