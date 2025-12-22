"""Centralised test data for both conftest.py and seed_database.py"""

from tests.utils.test_data.basics import *
from tests.utils.test_data.data_tables import *
from tests.utils.test_data.job_rating_service import *
from tests.utils.test_data.job_scraping_service import *


def validate_ownership_integrity_detailed(data_collections: dict) -> dict:
    """Comprehensive function that checks ownership integrity across all relationships in the database.
    Validates that:
    1. All direct foreign key relationships respect owner boundaries
    2. All many-to-many mapping relationships respect owner boundaries
    3. Provides detailed reporting of violations and statistics
    :param data_collections: Dictionary containing all data collections"""

    results = {
        "direct_foreign_key_violations": [],
        "mapping_violations": [],
        "statistics": {
            "tables_checked": 0,
            "entries_validated": 0,
            "relationships_validated": 0,
            "users_found": set(),
        },
        "edge_cases": [],
        "summary": {},
    }

    # Helper functions
    def find_owner_by_id(collection_name: str, entry_id: int) -> int | None:
        """Find owner_id of an entry by its ID (1-based)
        :param collection_name: Name of the data collection
        :param entry_id: 1-based ID of the entry"""

        collection = data_collections.get(collection_name, [])
        if isinstance(entry_id, (int, float)) and 1 <= entry_id <= len(collection):
            entry_ = collection[int(entry_id) - 1]  # Convert to 0-based index
            ownerid = entry_.get("owner_id")
            if ownerid is not None:
                results["statistics"]["users_found"].add(ownerid)
            return ownerid
        return None

    def log_edge_case(case_type: str, description: str, details: dict) -> None:
        """Log edge cases for analysis
        :param case_type: Type of edge case
        :param description: Description of the edge case
        :param details: Additional details about the case"""

        results["edge_cases"].append({"type": case_type, "description": description, "details": details})

    # Define all foreign key relationships
    fk_relationships = {
        "PERSON_DATA": [("company_id", "COMPANY_DATA", "optional")],  # Can be None
        "JOB_DATA": [
            ("company_id", "COMPANY_DATA", "optional"),
            ("location_id", "LOCATION_DATA", "optional"),
            ("source_id", "AGGREGATOR_DATA", "optional"),
            ("cv_id", "FILE_DATA", "optional"),
            ("cover_letter_id", "FILE_DATA", "optional"),
            ("application_aggregator_id", "AGGREGATOR_DATA", "optional"),
        ],
        "INTERVIEW_DATA": [
            ("location_id", "LOCATION_DATA", "optional"),
            ("job_id", "JOB_DATA", "required"),  # Should always have a job
        ],
        "JOB_APPLICATION_UPDATE_DATA": [("job_id", "JOB_DATA", "required")],  # Should always reference a job
    }

    print("=== OWNERSHIP INTEGRITY VALIDATION ===\n")

    # Phase 1: Validate direct foreign key relationships
    print("Phase 1: Validating direct foreign key relationships...")

    for table_name, relationships in fk_relationships.items():
        table_data = data_collections.get(table_name, [])
        if not table_data:
            continue

        results["statistics"]["tables_checked"] += 1
        print(f"  Checking {table_name}: {len(table_data)} entries")

        for entry_idx, entry in enumerate(table_data):
            results["statistics"]["entries_validated"] += 1
            entry_owner = entry.get("owner_id")

            # Track users
            if entry_owner is not None:
                results["statistics"]["users_found"].add(entry_owner)

            for fk_field, referenced_table, constraint in relationships:
                results["statistics"]["relationships_validated"] += 1
                fk_value = entry.get(fk_field)

                # Handle different constraint types
                if constraint == "required" and fk_value is None:
                    log_edge_case(
                        "missing_required_fk",
                        f"Required foreign key {fk_field} is None",
                        {"table": table_name, "entry_idx": entry_idx + 1},
                    )
                    continue

                if fk_value is not None:
                    referenced_owner = find_owner_by_id(referenced_table, fk_value)

                    if referenced_owner is None:
                        log_edge_case(
                            "invalid_fk_reference",
                            f"Foreign key {fk_field} references non-existent entry",
                            {
                                "table": table_name,
                                "entry_idx": entry_idx + 1,
                                "fk_value": fk_value,
                                "referenced_table": referenced_table,
                            },
                        )
                        continue

                    if referenced_owner != entry_owner:
                        results["direct_foreign_key_violations"].append(
                            {
                                "severity": "HIGH",
                                "table": table_name,
                                "entry_index": entry_idx + 1,
                                "entry_data": {
                                    k: v for k, v in entry.items() if k not in ["description", "body"]
                                },  # Exclude long text
                                "entry_owner": entry_owner,
                                "field": fk_field,
                                "referenced_id": fk_value,
                                "referenced_table": referenced_table,
                                "referenced_owner": referenced_owner,
                                "violation_type": "cross_user_reference",
                                "message": f"User {entry_owner} entry references {referenced_table} owned by user {referenced_owner}",
                            }
                        )

    # Phase 2: Validate mapping relationships
    print(f"\nPhase 2: Validating mapping relationships...")

    mapping_relationships = {
        "JOB_KEYWORD_MAPPINGS": {
            "primary_table": "JOB_DATA",
            "primary_id_field": "job_id",
            "secondary_table": "KEYWORD_DATA",
            "secondary_ids_field": "keyword_ids",
            "description": "Job-Keyword associations",
        },
        "JOB_CONTACT_MAPPINGS": {
            "primary_table": "JOB_DATA",
            "primary_id_field": "job_id",
            "secondary_table": "PERSON_DATA",
            "secondary_ids_field": "person_ids",
            "description": "Job-Contact person associations",
        },
        "INTERVIEW_INTERVIEWER_MAPPINGS": {
            "primary_table": "INTERVIEW_DATA",
            "primary_id_field": "interview_id",
            "secondary_table": "PERSON_DATA",
            "secondary_ids_field": "person_ids",
            "description": "Interview-Interviewer associations",
        },
        "EMAIL_SCRAPEDJOB_MAPPINGS": {
            "primary_table": "JOB_ALERT_EMAIL_DATA",
            "primary_id_field": "email_id",
            "secondary_table": "JOB_SCRAPED_DATA",
            "secondary_ids_field": "scraped_job_ids",
            "description": "Email-Scraped job associations",
        },
    }

    for mapping_name, config in mapping_relationships.items():
        mapping_data = data_collections.get(mapping_name, [])
        if not mapping_data:
            continue

        print(f"  Checking {mapping_name}: {len(mapping_data)} mappings - {config['description']}")

        for mapping_idx, mapping in enumerate(mapping_data):
            primary_id = mapping.get(config["primary_id_field"])
            secondary_ids = mapping.get(config["secondary_ids_field"], [])

            if primary_id is None:
                log_edge_case(
                    "missing_primary_id",
                    f"Mapping missing primary ID {config['primary_id_field']}",
                    {"mapping_table": mapping_name, "mapping_idx": mapping_idx + 1},
                )
                continue

            primary_owner = find_owner_by_id(config["primary_table"], primary_id)

            if primary_owner is None:
                log_edge_case(
                    "invalid_primary_reference",
                    f"Mapping references non-existent primary entry",
                    {"mapping_table": mapping_name, "primary_id": primary_id},
                )
                continue

            for secondary_id in secondary_ids:
                results["statistics"]["relationships_validated"] += 1
                secondary_owner = find_owner_by_id(config["secondary_table"], secondary_id)

                if secondary_owner is None:
                    log_edge_case(
                        "invalid_secondary_reference",
                        f"Mapping references non-existent secondary entry",
                        {"mapping_table": mapping_name, "secondary_id": secondary_id},
                    )
                    continue

                if primary_owner != secondary_owner:
                    results["mapping_violations"].append(
                        {
                            "severity": "MEDIUM",
                            "mapping_table": mapping_name,
                            "mapping_index": mapping_idx + 1,
                            "mapping_data": mapping,
                            "primary_table": config["primary_table"],
                            "primary_id": primary_id,
                            "primary_owner": primary_owner,
                            "secondary_table": config["secondary_table"],
                            "secondary_id": secondary_id,
                            "secondary_owner": secondary_owner,
                            "violation_type": "cross_user_mapping",
                            "message": f"Mapping connects {config['primary_table']} (user {primary_owner}) with {config['secondary_table']} (user {secondary_owner})",
                        }
                    )

    # Phase 3: Generate comprehensive summary
    print(f"\nPhase 3: Generating summary report...")

    total_violations = len(results["direct_foreign_key_violations"]) + len(results["mapping_violations"])

    results["summary"] = {
        "validation_status": "PASS" if total_violations == 0 else "FAIL",
        "total_violations": total_violations,
        "high_severity_violations": len(results["direct_foreign_key_violations"]),
        "medium_severity_violations": len(results["mapping_violations"]),
        "edge_cases_found": len(results["edge_cases"]),
        "tables_validated": results["statistics"]["tables_checked"],
        "entries_validated": results["statistics"]["entries_validated"],
        "relationships_validated": results["statistics"]["relationships_validated"],
        "unique_users": len(results["statistics"]["users_found"]),
        "user_ids_found": sorted(list(results["statistics"]["users_found"])),
    }

    return results


analysis_results = validate_ownership_integrity_detailed(
    {
        "COMPANY_DATA": COMPANY_DATA,
        "LOCATION_DATA": LOCATION_DATA,
        "PERSON_DATA": PERSON_DATA,
        "JOB_DATA": JOB_DATA,
        "INTERVIEW_DATA": INTERVIEW_DATA,
        "FILE_DATA": FILE_DATA,
        "KEYWORD_DATA": KEYWORD_DATA,
        "AGGREGATOR_DATA": AGGREGATOR_DATA,
        "JOB_APPLICATION_UPDATE_DATA": JOB_APPLICATION_UPDATE_DATA,
        "JOB_ALERT_EMAIL_DATA": JOB_EMAIL_DATA,
        "JOB_SCRAPED_DATA": SCRAPED_JOB_DATA,
        "JOB_KEYWORD_MAPPINGS": JOB_KEYWORD_MAPPINGS,
        "JOB_CONTACT_MAPPINGS": JOB_CONTACT_MAPPINGS,
        "INTERVIEW_INTERVIEWER_MAPPINGS": INTERVIEW_INTERVIEWER_MAPPINGS,
        "EMAIL_SCRAPEDJOB_MAPPINGS": EMAIL_SCRAPEDJOB_MAPPINGS,
    }
)


if analysis_results["summary"]["validation_status"] == "FAIL":
    print("\n=== DETAILED VIOLATION REPORT ===\n")

    if analysis_results["direct_foreign_key_violations"]:
        print("Direct Foreign Key Violations:")
        for violation in analysis_results["direct_foreign_key_violations"]:
            print(violation)

    if analysis_results["mapping_violations"]:
        print("\nMapping Violations:")
        for violation in analysis_results["mapping_violations"]:
            print(violation)

    if analysis_results["edge_cases"]:
        print("\nEdge Cases:")
        for edge_case in analysis_results["edge_cases"]:
            print(edge_case)

    raise AssertionError("Ownership integrity validation failed - see report above.")
