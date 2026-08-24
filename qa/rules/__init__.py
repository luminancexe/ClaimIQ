"""QA Rules Package for ClaimIQ Phase 5."""

from qa.rules.completeness import COMPLETENESS_RULES, evaluate_completeness_rule
from qa.rules.duplication import DUPLICATION_RULES, evaluate_duplication_rule
from qa.rules.referential import REFERENTIAL_RULES, evaluate_referential_rule
from qa.rules.financial import FINANCIAL_RULES, evaluate_financial_rule
from qa.rules.temporal import TEMPORAL_RULES, evaluate_temporal_rule
from qa.rules.lifecycle import LIFECYCLE_RULES, evaluate_lifecycle_rule
from qa.rules.business_logic import BUSINESS_LOGIC_RULES, evaluate_business_logic_rule
from qa.rules.formatting import FORMATTING_RULES, evaluate_formatting_rule

ALL_RULE_DEFINITIONS = (
    COMPLETENESS_RULES +
    DUPLICATION_RULES +
    REFERENTIAL_RULES +
    FINANCIAL_RULES +
    TEMPORAL_RULES +
    LIFECYCLE_RULES +
    BUSINESS_LOGIC_RULES +
    FORMATTING_RULES
)

RULE_EVALUATOR_MAP = {}
for r in COMPLETENESS_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_completeness_rule
for r in DUPLICATION_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_duplication_rule
for r in REFERENTIAL_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_referential_rule
for r in FINANCIAL_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_financial_rule
for r in TEMPORAL_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_temporal_rule
for r in LIFECYCLE_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_lifecycle_rule
for r in BUSINESS_LOGIC_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_business_logic_rule
for r in FORMATTING_RULES:
    RULE_EVALUATOR_MAP[r.rule_code] = evaluate_formatting_rule
