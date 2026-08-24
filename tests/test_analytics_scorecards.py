"""Unit tests for Provider Quality Scorecards and Payer Adjudication Scorecards."""

from decimal import Decimal
import pytest
from analytics.models import ProviderScorecard, PayerScorecard
from analytics.scorecards import generate_provider_scorecards, generate_payer_scorecards


def test_provider_scorecard_defaults():
    cards = generate_provider_scorecards(conn=None)
    assert len(cards) == 1
    p = cards[0]
    assert p.provider_id == 1
    assert p.provider_reference == "PRV-2026-0000001"
    assert p.specialty == "Internal Medicine"
    assert p.claim_volume == 150
    assert p.total_billed == Decimal("37500.00")
    assert p.dq_score == 100.0


def test_payer_scorecard_defaults():
    cards = generate_payer_scorecards(conn=None)
    assert len(cards) == 1
    py = cards[0]
    assert py.payer_id == 1
    assert py.payer_reference == "PAY-2026-0000001"
    assert py.payer_type == "Commercial"
    assert py.claim_volume == 300
    assert py.average_adjudication_latency_days == 5.20
    assert py.average_payment_latency_days == 7.40
    assert py.timely_filing_compliance_rate == 100.0


def test_provider_scorecard_serialization():
    card = ProviderScorecard(
        provider_id=10,
        provider_reference="PRV-2026-0000010",
        provider_name="Dr. Jane Miller",
        specialty="Cardiology",
        facility_id=2,
        facility_name="Heart Center",
        claim_volume=200,
        total_billed=Decimal("50000.00"),
        total_paid=Decimal("40000.00"),
        payment_rate=80.00,
        denial_rate=4.00,
        issue_count=2,
        issue_density=0.0100,
        dq_score=98.00,
        financial_exposure=Decimal("0.00"),
    )
    d = card.to_dict()
    assert d["provider_reference"] == "PRV-2026-0000010"
    assert d["specialty"] == "Cardiology"
    assert d["total_billed"] == "50000.00"
    assert d["dq_score"] == 98.0


def test_payer_scorecard_serialization():
    card = PayerScorecard(
        payer_id=3,
        payer_reference="PAY-2026-0000003",
        payer_name="Medicare Part B",
        payer_type="Medicare",
        claim_volume=500,
        total_billed=Decimal("125000.00"),
        total_paid=Decimal("100000.00"),
        denial_rate=3.50,
        payment_rate=80.00,
        average_adjudication_latency_days=4.10,
        average_payment_latency_days=6.20,
        timely_filing_compliance_rate=99.50,
        contractual_adjustment_ratio=18.00,
        issue_count=1,
    )
    d = card.to_dict()
    assert d["payer_name"] == "Medicare Part B"
    assert d["contractual_adjustment_ratio"] == 18.0
    assert d["average_adjudication_latency_days"] == 4.10
    assert d["timely_filing_compliance_rate"] == 99.50
