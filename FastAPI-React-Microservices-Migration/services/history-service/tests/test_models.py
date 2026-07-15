from sqlmodel import Session, SQLModel, create_engine, select

from app.models import OperationRecord


def make_test_engine(tmp_path):
    db_file = tmp_path / "test_history.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def test_insert_and_query_round_trip(tmp_path):
    engine = make_test_engine(tmp_path)
    with Session(engine) as session:
        record = OperationRecord(
            operation="sum",
            operand_a=2,
            operand_b=3,
            result=5,
            mode="monolith",
            handled_by="monolith",
            correlation_id="abc-123",
            latency_ms=1.5,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        assert record.id is not None

    with Session(engine) as session:
        fetched = session.exec(select(OperationRecord)).all()
        assert len(fetched) == 1
        assert fetched[0].operation == "sum"
        assert fetched[0].result == 5
        assert fetched[0].mode == "monolith"
        assert fetched[0].created_at is not None
