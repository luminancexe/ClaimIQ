#!/usr/bin/env python3
"""
ClaimIQ — MySQL 8.x Database Schema Validation Suite
Validates the official relational DDL against a live MySQL 8.x test database.

Tests Executed:
1. Database Connection & Environment Isolation (claimiq_test)
2. Deterministic DDL Schema Execution (Tables, Primary Keys, Foreign Keys, Indexes)
3. Table Existence & Column Count Verification (22 core tables)
4. Reference Data Population Verification (Statuses, Severities, DQ Dimensions, Root Causes)
5. Valid Transactional Data Insertion & Relational Integrity
6. Constraint Enforcement:
   - Rejection of Orphan Foreign Keys (Referential Integrity)
   - Rejection of Duplicate Unique Keys (Uniqueness)
   - Rejection of NOT NULL Violations (Completeness)
   - Rejection of Negative Values via CHECK Constraints (Financial/Validity)
7. Deterministic Teardown & Clean Schema Rebuild
"""

import os
import sys
import argparse
import pymysql
from pymysql.constants import CLIENT


EXPECTED_TABLES = [
    "ref_claim_statuses",
    "ref_issue_statuses",
    "ref_severities",
    "ref_dq_dimensions",
    "ref_root_causes",
    "ref_adjustment_group_codes",
    "patients",
    "facilities",
    "providers",
    "payers",
    "insurance_plans",
    "patient_coverage",
    "encounters",
    "encounter_diagnoses",
    "claims",
    "claim_lines",
    "claim_status_history",
    "remittances",
    "payments",
    "adjustments",
    "denials",
    "reconciliations",
    "qa_rule_categories",
    "qa_rules",
    "qa_execution_runs",
    "qa_results",
    "issues",
    "issue_history",
    "issue_notes",
    "audit_events",
]


class MySQLSchemaValidator:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.results = []

    def log_result(self, test_name, status, details=""):
        symbol = "✓ PASS" if status else "✗ FAIL"
        self.results.append((test_name, status, details))
        print(f"[{symbol}] {test_name}: {details}")

    def connect(self):
        try:
            # Connect to server with multi-statement support
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                client_flag=CLIENT.MULTI_STATEMENTS,
                autocommit=True
            )
            print(f"Successfully connected to MySQL server at {self.host}:{self.port} as '{self.user}'.")
            return True
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to connect to MySQL 8.x server: {e}")
            print("Please ensure MySQL 8.x is running and provide valid credentials via arguments or environment variables.")
            return False

    def setup_test_database(self):
        cursor = self.connection.cursor()
        print(f"Creating isolated test database `{self.database}`...")
        cursor.execute(f"DROP DATABASE IF EXISTS `{self.database}`")
        cursor.execute(f"CREATE DATABASE `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        cursor.execute(f"USE `{self.database}`")
        cursor.close()
        self.log_result("Test Database Isolation", True, f"Database `{self.database}` created clean.")

    def execute_migration_ddl(self, migration_file_path):
        if not os.path.exists(migration_file_path):
            self.log_result("Migration File Exists", False, f"File not found: {migration_file_path}")
            return False

        with open(migration_file_path, "r", encoding="utf-8") as f:
            ddl_script = f.read()

        cursor = self.connection.cursor()
        try:
            cursor.execute(ddl_script)
            # Consume all multi-statement result sets
            while cursor.nextset():
                pass
            cursor.close()
            self.log_result("DDL Migration Execution", True, "001_initial_schema.sql executed successfully.")
            return True
        except Exception as e:
            cursor.close()
            self.log_result("DDL Migration Execution", False, f"Error executing DDL: {e}")
            return False

    def verify_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [row[0].lower() for row in cursor.fetchall()]
        cursor.close()

        missing = [t for t in EXPECTED_TABLES if t.lower() not in existing_tables]
        if not missing:
            self.log_result("Table Existence Verification", True, f"All {len(EXPECTED_TABLES)} expected tables exist.")
        else:
            self.log_result("Table Existence Verification", False, f"Missing tables: {missing}")

    def verify_reference_seeds(self):
        cursor = self.connection.cursor()
        checks = [
            ("ref_claim_statuses", 7),
            ("ref_issue_statuses", 7),
            ("ref_severities", 4),
            ("ref_dq_dimensions", 7),
            ("ref_root_causes", 7),
            ("ref_adjustment_group_codes", 5),
            ("qa_rule_categories", 7)
        ]
        all_passed = True
        details = []
        for table, expected_count in checks:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            if count != expected_count:
                all_passed = False
                details.append(f"{table}: got {count}, expected {expected_count}")
            else:
                details.append(f"{table}: {count} rows")
        cursor.close()
        self.log_result("Reference Seed Verification", all_passed, ", ".join(details))

    def test_valid_inserts(self):
        cursor = self.connection.cursor()
        try:
            # 1. Patient
            cursor.execute("""
                INSERT INTO patients (patient_reference, first_name, last_name, date_of_birth, gender, address_state)
                VALUES ('PAT-TEST-001', 'John', 'Doe', '1985-04-12', 'MALE', 'CA')
            """)
            patient_id = cursor.lastrowid

            # 2. Facility
            cursor.execute("""
                INSERT INTO facilities (facility_reference, facility_name, tin, facility_type, state)
                VALUES ('FAC-TEST-001', 'General Medical Center', '123456789', 'Outpatient Clinic', 'CA')
            """)
            facility_id = cursor.lastrowid

            # 3. Provider
            cursor.execute("""
                INSERT INTO providers (provider_reference, facility_id, first_name, last_name, npi, taxonomy_code, specialty)
                VALUES ('PRV-TEST-001', %s, 'Sarah', 'Smith', '1982736450', '207Q00000X', 'Internal Medicine')
            """, (facility_id,))
            provider_id = cursor.lastrowid

            # 4. Payer & Plan
            cursor.execute("""
                INSERT INTO payers (payer_reference, payer_name, payer_type, timely_filing_days)
                VALUES ('PAY-TEST-001', 'Blue Cross Commercial', 'Commercial', 365)
            """)
            payer_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO insurance_plans (payer_id, plan_name, plan_type)
                VALUES (%s, 'Blue Advantage PPO', 'PPO')
            """, (payer_id,))
            plan_id = cursor.lastrowid

            # 5. Encounter
            cursor.execute("""
                INSERT INTO encounters (encounter_reference, patient_id, provider_id, facility_id, date_of_service, encounter_type)
                VALUES ('ENC-TEST-001', %s, %s, %s, '2026-08-15', 'Outpatient')
            """, (patient_id, provider_id, facility_id))
            encounter_id = cursor.lastrowid

            # 6. Claim Header
            cursor.execute("""
                INSERT INTO claims (claim_reference, encounter_id, patient_id, billing_provider_id, payer_id, current_status_code, total_billed_amount, submission_date)
                VALUES ('CLM-TEST-001', %s, %s, %s, %s, 'Submitted', 250.00, '2026-08-16')
            """, (encounter_id, patient_id, provider_id, payer_id))
            claim_id = cursor.lastrowid

            # 7. Claim Line
            cursor.execute("""
                INSERT INTO claim_lines (claim_id, line_number, cpt_code, procedure_description, units, unit_price, line_billed_amount)
                VALUES (%s, 1, '99214', 'Office Visit Level 4', 1.00, 250.00, 250.00)
            """, (claim_id,))

            # 8. Remittance & Payment
            cursor.execute("""
                INSERT INTO remittances (remittance_reference, payer_id, check_trace_number, payment_method, total_paid_amount, remittance_date)
                VALUES ('REM-TEST-001', %s, 'CHK-987654321', 'EFT', 200.00, '2026-08-20')
            """, (payer_id,))
            remittance_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO payments (payment_reference, remittance_id, claim_id, paid_amount, payment_date)
                VALUES ('PMT-TEST-001', %s, %s, 200.00, '2026-08-20')
            """, (remittance_id, claim_id))

            # 9. Adjustment
            cursor.execute("""
                INSERT INTO adjustments (claim_id, group_code, reason_code, adjustment_amount, adjustment_description)
                VALUES (%s, 'CO', '45', 50.00, 'Charge exceeds fee schedule')
            """, (claim_id,))

            # 10. Reconciliation
            cursor.execute("""
                INSERT INTO reconciliations (claim_id, total_billed, total_paid, total_adjusted, total_patient_resp, variance_amount, reconciliation_status)
                VALUES (%s, 250.00, 200.00, 50.00, 0.00, 0.00, 'BALANCED')
            """, (claim_id,))

            cursor.close()
            self.log_result("Valid Relational Insert Pipeline", True, "All entities inserted and linked cleanly.")
            return True
        except Exception as e:
            cursor.close()
            self.log_result("Valid Relational Insert Pipeline", False, f"Insert failed: {e}")
            return False

    def test_invalid_foreign_key(self):
        cursor = self.connection.cursor()
        try:
            # Attempt inserting claim with non-existent patient ID
            cursor.execute("""
                INSERT INTO claims (claim_reference, encounter_id, patient_id, billing_provider_id, payer_id, current_status_code, total_billed_amount, submission_date)
                VALUES ('CLM-INVALID-001', 1, 9999999, 1, 1, 'Submitted', 100.00, '2026-08-16')
            """)
            cursor.close()
            self.log_result("Foreign Key Rejection Test", False, "Orphan foreign key was mistakenly accepted!")
        except pymysql.err.IntegrityError as e:
            cursor.close()
            self.log_result("Foreign Key Rejection Test", True, f"Orphan foreign key correctly rejected ({e.args[0]}).")

    def test_duplicate_unique_constraint(self):
        cursor = self.connection.cursor()
        try:
            # Duplicate patient_reference
            cursor.execute("""
                INSERT INTO patients (patient_reference, first_name, last_name, date_of_birth, gender, address_state)
                VALUES ('PAT-TEST-001', 'Jane', 'Duplicate', '1990-01-01', 'FEMALE', 'NY')
            """)
            cursor.close()
            self.log_result("Unique Constraint Rejection Test", False, "Duplicate patient_reference was mistakenly accepted!")
        except pymysql.err.IntegrityError as e:
            cursor.close()
            self.log_result("Unique Constraint Rejection Test", True, f"Duplicate unique value correctly rejected ({e.args[0]}).")

    def test_not_null_constraint(self):
        cursor = self.connection.cursor()
        try:
            # NULL date_of_birth
            cursor.execute("""
                INSERT INTO patients (patient_reference, first_name, last_name, date_of_birth, gender, address_state)
                VALUES ('PAT-TEST-NONULL', 'Jane', 'NoDOB', NULL, 'FEMALE', 'NY')
            """)
            cursor.close()
            self.log_result("NOT NULL Constraint Test", False, "NULL date_of_birth was mistakenly accepted!")
        except pymysql.err.OperationalError as e:
            cursor.close()
            self.log_result("NOT NULL Constraint Test", True, f"NOT NULL violation correctly rejected ({e.args[0]}).")
        except pymysql.err.IntegrityError as e:
            cursor.close()
            self.log_result("NOT NULL Constraint Test", True, f"NOT NULL violation correctly rejected ({e.args[0]}).")

    def test_check_constraint(self):
        cursor = self.connection.cursor()
        try:
            # Negative billed amount
            cursor.execute("""
                INSERT INTO claims (claim_reference, encounter_id, patient_id, billing_provider_id, payer_id, current_status_code, total_billed_amount, submission_date)
                VALUES ('CLM-NEG-001', 1, 1, 1, 1, 'Submitted', -150.00, '2026-08-16')
            """)
            cursor.close()
            self.log_result("CHECK Constraint Enforcement Test", False, "Negative total_billed_amount was mistakenly accepted!")
        except (pymysql.err.OperationalError, pymysql.err.IntegrityError) as e:
            cursor.close()
            self.log_result("CHECK Constraint Enforcement Test", True, f"Negative billed amount correctly rejected by CHECK constraint ({e.args[0]}).")

    def test_reproducible_rebuild(self, migration_file_path):
        cursor = self.connection.cursor()
        print("Testing deterministic teardown and rebuild...")
        cursor.execute(f"DROP DATABASE IF EXISTS `{self.database}`")
        cursor.execute(f"CREATE DATABASE `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        cursor.execute(f"USE `{self.database}`")
        cursor.close()

        success = self.execute_migration_ddl(migration_file_path)
        if success:
            self.log_result("Deterministic Rebuild Test", True, "Database successfully dropped and recreated from migration script.")
        else:
            self.log_result("Deterministic Rebuild Test", False, "Failed to rebuild database from migration script.")

    def run_all(self, migration_file_path):
        print("====================================================================")
        print("ClaimIQ Phase 2: MySQL 8.x Schema Validation Runner")
        print("====================================================================")
        if not self.connect():
            return False

        try:
            self.setup_test_database()
            if not self.execute_migration_ddl(migration_file_path):
                return False

            self.verify_tables()
            self.verify_reference_seeds()
            self.test_valid_inserts()
            self.test_invalid_foreign_key()
            self.test_duplicate_unique_constraint()
            self.test_not_null_constraint()
            self.test_check_constraint()
            self.test_reproducible_rebuild(migration_file_path)

            all_passed = all(status for _, status, _ in self.results)
            print("====================================================================")
            print(f"Validation Summary: {sum(1 for _, s, _ in self.results if s)}/{len(self.results)} Tests Passed.")
            if all_passed:
                print("SUCCESS: Phase 2 MySQL 8.x Schema Validation PASSED completely.")
            else:
                print("FAILURE: One or more schema validation checks failed.")
            print("====================================================================")
            return all_passed
        finally:
            if self.connection:
                self.connection.close()


def main():
    parser = argparse.ArgumentParser(description="ClaimIQ MySQL 8.x Schema Validation Suite")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "127.0.0.1"), help="MySQL Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", "3306")), help="MySQL Port (default: 3306)")
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"), help="MySQL User (default: root)")
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", ""), help="MySQL Password")
    parser.add_argument("--database", default=os.getenv("MYSQL_DATABASE", "claimiq_test"), help="Test Database Name (default: claimiq_test)")
    parser.add_argument("--migration", default=os.path.join(os.path.dirname(__file__), "migrations", "001_initial_schema.sql"), help="Path to 001_initial_schema.sql")

    args = parser.parse_args()
    validator = MySQLSchemaValidator(args.host, args.port, args.user, args.password, args.database)
    success = validator.run_all(args.migration)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
