"""ClaimIQ Anomaly Mutators Package."""

from generator.injector.mutators.completeness import mutate_completeness
from generator.injector.mutators.duplication import mutate_duplication
from generator.injector.mutators.referential import mutate_referential
from generator.injector.mutators.financial import mutate_financial
from generator.injector.mutators.temporal import mutate_temporal
from generator.injector.mutators.lifecycle import mutate_lifecycle
from generator.injector.mutators.business_logic import mutate_business_logic
from generator.injector.mutators.formatting import mutate_formatting

MUTATOR_DISPATCH = {
    "E001": mutate_completeness,
    "E002": mutate_completeness,
    "E003": mutate_completeness,
    "E004": mutate_completeness,
    "E005": mutate_completeness,
    "E006": mutate_completeness,
    "E007": mutate_completeness,
    "E008": mutate_completeness,
    "E009": mutate_completeness,
    "E010": mutate_completeness,

    "E011": mutate_duplication,
    "E012": mutate_duplication,
    "E013": mutate_duplication,
    "E014": mutate_duplication,
    "E015": mutate_duplication,

    "E016": mutate_referential,
    "E017": mutate_referential,
    "E018": mutate_referential,
    "E019": mutate_referential,
    "E020": mutate_referential,
    "E021": mutate_referential,
    "E022": mutate_referential,

    "E023": mutate_financial,
    "E024": mutate_financial,
    "E025": mutate_financial,
    "E026": mutate_financial,
    "E027": mutate_financial,
    "E028": mutate_financial,
    "E029": mutate_financial,
    "E030": mutate_financial,
    "E031": mutate_financial,
    "E032": mutate_financial,
    "E033": mutate_financial,

    "E034": mutate_temporal,
    "E035": mutate_temporal,
    "E036": mutate_temporal,
    "E037": mutate_temporal,
    "E038": mutate_temporal,
    "E039": mutate_temporal,
    "E040": mutate_temporal,
    "E041": mutate_temporal,
    "E042": mutate_temporal,

    "E043": mutate_lifecycle,
    "E044": mutate_lifecycle,
    "E045": mutate_lifecycle,
    "E046": mutate_lifecycle,
    "E047": mutate_lifecycle,
    "E048": mutate_lifecycle,
    "E049": mutate_lifecycle,
    "E050": mutate_lifecycle,

    "E051": mutate_business_logic,
    "E052": mutate_business_logic,
    "E053": mutate_business_logic,
    "E054": mutate_business_logic,
    "E055": mutate_business_logic,
    "E056": mutate_business_logic,
    "E057": mutate_business_logic,
    "E058": mutate_business_logic,
    "E059": mutate_business_logic,
    "E060": mutate_business_logic,

    "E061": mutate_formatting,
    "E062": mutate_formatting,
    "E063": mutate_formatting,
    "E064": mutate_formatting,
    "E065": mutate_formatting,
    "E066": mutate_formatting,
    "E067": mutate_formatting,
}
