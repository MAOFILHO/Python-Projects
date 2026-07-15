from common.correlation import CORRELATION_HEADER, get_or_create_correlation_id
from common.schemas import HealthResponse
from common.trace import TraceHop, make_hop, timed_hop
from datetime import datetime, timezone


def test_timed_hop_records_duration_and_status_ok():
    with timed_hop("sum-service", "compute_sum") as builder:
        total = sum(range(100))
    assert total == 4950
    hop = builder.hop
    assert isinstance(hop, TraceHop)
    assert hop.service == "sum-service"
    assert hop.action == "compute_sum"
    assert hop.status == "ok"
    assert hop.duration_ms >= 0


def test_timed_hop_records_error_status_and_reraises():
    try:
        with timed_hop("sum-service", "compute_sum") as builder:
            raise ValueError("boom")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError to propagate")
    assert builder.hop is not None
    assert builder.hop.status == "error"


def test_make_hop_builds_trace_hop_directly():
    hop = make_hop("monolith", "compute_mul", datetime.now(timezone.utc), 1.23)
    assert hop.service == "monolith"
    assert hop.action == "compute_mul"
    assert hop.duration_ms == 1.23
    assert hop.status == "ok"


def test_get_or_create_correlation_id_uses_existing_header():
    headers = {CORRELATION_HEADER: "abc-123"}
    assert get_or_create_correlation_id(headers) == "abc-123"


def test_get_or_create_correlation_id_generates_when_missing():
    cid = get_or_create_correlation_id({})
    assert isinstance(cid, str)
    assert len(cid) > 0


def test_health_response_schema():
    resp = HealthResponse(service="sum-service", status="ok", version="0.1.0")
    assert resp.status == "ok"
