from dataclasses import dataclass
from math import ceil

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    size: int = 20

    def __post_init__(self) -> None:
        object.__setattr__(self, "page", max(self.page, 1))
        object.__setattr__(self, "size", min(max(self.size, 1), MAX_PAGE_SIZE))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(ceil(self.total / self.size), 1)

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


def paginate[T](session: Session, statement: Select[tuple[T]], params: PageParams) -> Page[T]:
    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = session.scalar(count_statement) or 0
    items = session.scalars(statement.limit(params.size).offset(params.offset)).all()
    return Page(items=list(items), total=total, page=params.page, size=params.size)
