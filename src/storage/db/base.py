from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


my_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_N_label)s",
        "uq": "%(table_name)s_%(column_0_N_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
        "pk": "%(table_name)s_pkey",
    }
)


class Model(AsyncAttrs, DeclarativeBase):
    metadata = my_metadata


class RecordModelMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.id == __value.id

    def __hash__(self) -> int:
        return self.id


class IncrementRecordModelMixin(RecordModelMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


__all__ = [
    "Model",
    "RecordModelMixin",
    "IncrementRecordModelMixin",
]
