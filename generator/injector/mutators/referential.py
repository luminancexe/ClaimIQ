"""Referential & Cross-Entity Anomaly Mutators (E016–E022)."""

from typing import List, Dict, Any
import pymysql
from generator.random_state import GeneratorRandomState
from generator.injector.models import GroundTruthRecord
from generator.injector.taxonomy import TAXONOMY


def mutate_referential(
    conn: pymysql.Connection,
    anomaly_code: str,
    count: int,
    rng: GeneratorRandomState,
    profile_name: str,
    seed: int,
    dry_run: bool = False,
) -> List[GroundTruthRecord]:
    """Execute referential mutations (E016–E022)."""
    defn = TAXONOMY[anomaly_code]
    records: List[GroundTruthRecord] = []

    with conn.cursor() as cur:
        if anomaly_code == "E016":
            # Provider facility state mismatch
            cur.execute("""
                SELECT p.provider_id, p.provider_reference, p.facility_id, f.state AS fac_state
                FROM providers p
                JOIN facilities f ON p.facility_id = f.facility_id
                ORDER BY p.provider_id
            """)
            prov_rows = cur.fetchall()
            cur.execute("SELECT facility_id, state FROM facilities ORDER BY facility_id")
            fac_rows = cur.fetchall()
            if not prov_rows or len(fac_rows) < 2:
                return records

            selected = rng.sample(prov_rows, min(count, len(prov_rows)))
            for row in selected:
                # Find facility in different state
                diff_facs = [f["facility_id"] for f in fac_rows if f["state"] != row["fac_state"]]
                target_fac = rng.choice(diff_facs) if diff_facs else fac_rows[0]["facility_id"]
                
                if not dry_run:
                    cur.execute("UPDATE providers SET facility_id = %s WHERE provider_id = %s", (target_fac, row["provider_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="providers",
                    target_record_id=row["provider_id"],
                    target_business_reference=row["provider_reference"],
                    target_column="facility_id",
                    original_value=str(row["facility_id"]),
                    mutated_value=str(target_fac),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Provider facility reassigned to facility {target_fac} in disjoint state",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E017":
            # Payer insurance plan mismatch
            cur.execute("SELECT claim_id, claim_reference, payer_id FROM claims ORDER BY claim_id")
            claims = cur.fetchall()
            cur.execute("SELECT payer_id FROM payers ORDER BY payer_id")
            all_payers = [r["payer_id"] for r in cur.fetchall()]
            if not claims or len(all_payers) < 2:
                return records

            selected = rng.sample(claims, min(count, len(claims)))
            for row in selected:
                other_payers = [p for p in all_payers if p != row["payer_id"]]
                new_payer = rng.choice(other_payers) if other_payers else all_payers[0]
                if not dry_run:
                    cur.execute("UPDATE claims SET payer_id = %s WHERE claim_id = %s", (new_payer, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="payer_id",
                    original_value=str(row["payer_id"]),
                    mutated_value=str(new_payer),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim payer changed from {row['payer_id']} to {new_payer} discordant with policy plan",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E018":
            # Encounter provider specialty mismatch
            cur.execute("""
                SELECT e.encounter_id, e.encounter_reference, e.provider_id
                FROM encounters e
                WHERE e.encounter_type = 'Inpatient Hospital'
                ORDER BY e.encounter_id
            """)
            encs = cur.fetchall()
            if not encs:
                cur.execute("SELECT encounter_id, encounter_reference, provider_id FROM encounters ORDER BY encounter_id")
                encs = cur.fetchall()
            cur.execute("SELECT provider_id FROM providers WHERE specialty IN ('Dermatology', 'Psychiatry', 'Physical Therapy') ORDER BY provider_id")
            spec_provs = [r["provider_id"] for r in cur.fetchall()]
            if not spec_provs:
                cur.execute("SELECT provider_id FROM providers ORDER BY provider_id")
                spec_provs = [r["provider_id"] for r in cur.fetchall()]
            if not encs or not spec_provs:
                return records

            selected = rng.sample(encs, min(count, len(encs)))
            for row in selected:
                new_prov = rng.choice(spec_provs)
                if not dry_run:
                    cur.execute("UPDATE encounters SET provider_id = %s WHERE encounter_id = %s", (new_prov, row["encounter_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="encounters",
                    target_record_id=row["encounter_id"],
                    target_business_reference=row["encounter_reference"],
                    target_column="provider_id",
                    original_value=str(row["provider_id"]),
                    mutated_value=str(new_prov),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Encounter clinician updated to mismatched specialty provider {new_prov}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E019":
            # Patient policy payer mismatch
            cur.execute("""
                SELECT c.claim_id, c.claim_reference, c.patient_id, c.payer_id
                FROM claims c
                ORDER BY c.claim_id
            """)
            claims = cur.fetchall()
            cur.execute("SELECT payer_id FROM payers ORDER BY payer_id")
            all_payers = [r["payer_id"] for r in cur.fetchall()]
            if not claims or len(all_payers) < 2:
                return records

            selected = rng.sample(claims, min(count, len(claims)))
            for row in selected:
                # Find a payer where patient has no coverage
                cur.execute("""
                    SELECT ip.payer_id
                    FROM patient_coverage pc
                    JOIN insurance_plans ip ON pc.plan_id = ip.plan_id
                    WHERE pc.patient_id = %s
                """, (row["patient_id"],))
                patient_payers = {r["payer_id"] for r in cur.fetchall()}
                uncovered_payers = [p for p in all_payers if p not in patient_payers]
                target_payer = rng.choice(uncovered_payers) if uncovered_payers else rng.choice(all_payers)

                if not dry_run:
                    cur.execute("UPDATE claims SET payer_id = %s WHERE claim_id = %s", (target_payer, row["claim_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claims",
                    target_record_id=row["claim_id"],
                    target_business_reference=row["claim_reference"],
                    target_column="payer_id",
                    original_value=str(row["payer_id"]),
                    mutated_value=str(target_payer),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim submitted to payer {target_payer} where patient has no policy",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E020":
            # Claim line cross-claim linkage
            cur.execute("SELECT claim_line_id, claim_id FROM claim_lines ORDER BY claim_line_id")
            lines = cur.fetchall()
            cur.execute("SELECT claim_id FROM claims ORDER BY claim_id")
            all_claims = [r["claim_id"] for r in cur.fetchall()]
            if not lines or len(all_claims) < 2:
                return records

            selected = rng.sample(lines, min(count, len(lines)))
            for row in selected:
                other_claims = [c for c in all_claims if c != row["claim_id"]]
                target_claim = rng.choice(other_claims) if other_claims else all_claims[0]
                if not dry_run:
                    cur.execute("UPDATE claim_lines SET claim_id = %s WHERE claim_line_id = %s", (target_claim, row["claim_line_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="claim_lines",
                    target_record_id=row["claim_line_id"],
                    target_business_reference=f"LINE-{row['claim_line_id']}",
                    target_column="claim_id",
                    original_value=str(row["claim_id"]),
                    mutated_value=str(target_claim),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Claim line reallocated to disjoint claim {target_claim}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E021":
            # Payment allocated to discordant claim
            cur.execute("SELECT payment_id, payment_reference, claim_id FROM payments ORDER BY payment_id")
            pmts = cur.fetchall()
            cur.execute("SELECT claim_id FROM claims ORDER BY claim_id")
            all_claims = [r["claim_id"] for r in cur.fetchall()]
            if not pmts or len(all_claims) < 2:
                return records

            selected = rng.sample(pmts, min(count, len(pmts)))
            for row in selected:
                other_claims = [c for c in all_claims if c != row["claim_id"]]
                target_claim = rng.choice(other_claims) if other_claims else all_claims[0]
                if not dry_run:
                    cur.execute("UPDATE payments SET claim_id = %s WHERE payment_id = %s", (target_claim, row["payment_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="payments",
                    target_record_id=row["payment_id"],
                    target_business_reference=row["payment_reference"],
                    target_column="claim_id",
                    original_value=str(row["claim_id"]),
                    mutated_value=str(target_claim),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Payment allocated to discordant claim {target_claim}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

        elif anomaly_code == "E022":
            # Remittance payer mismatch with claim
            cur.execute("SELECT remittance_id, remittance_reference, payer_id FROM remittances ORDER BY remittance_id")
            remits = cur.fetchall()
            cur.execute("SELECT payer_id FROM payers ORDER BY payer_id")
            all_payers = [r["payer_id"] for r in cur.fetchall()]
            if not remits or len(all_payers) < 2:
                return records

            selected = rng.sample(remits, min(count, len(remits)))
            for row in selected:
                other_payers = [p for p in all_payers if p != row["payer_id"]]
                target_payer = rng.choice(other_payers) if other_payers else all_payers[0]
                if not dry_run:
                    cur.execute("UPDATE remittances SET payer_id = %s WHERE remittance_id = %s", (target_payer, row["remittance_id"]))

                rec = GroundTruthRecord(
                    anomaly_code=anomaly_code,
                    category_name=defn.category.value,
                    severity_code=defn.severity.value,
                    target_table="remittances",
                    target_record_id=row["remittance_id"],
                    target_business_reference=row["remittance_reference"],
                    target_column="payer_id",
                    original_value=str(row["payer_id"]),
                    mutated_value=str(target_payer),
                    injection_profile=profile_name,
                    injection_seed=seed,
                    description=f"Remittance payer updated to discordant payer {target_payer}",
                    expected_rule_category=defn.expected_rule_category,
                )
                records.append(rec)

    return records
