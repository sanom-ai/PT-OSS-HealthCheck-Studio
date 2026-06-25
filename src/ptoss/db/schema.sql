-- PT-OSS HealthCheck Studio initial PostgreSQL schema
-- Phase 0 baseline: tenant-scoped, audit-friendly, JSONB-enabled

CREATE TABLE IF NOT EXISTS organization (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessment_case (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    organization_id TEXT NOT NULL REFERENCES organization(id),
    state TEXT NOT NULL,
    rule_package_version TEXT NOT NULL,
    evidence_index_version TEXT NOT NULL,
    scope JSONB NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_document (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    source_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    source_uri TEXT,
    content_hash TEXT NOT NULL,
    document_type TEXT,
    category TEXT,
    owner TEXT,
    approver TEXT,
    revision TEXT,
    effective_date DATE,
    latest_update_date DATE,
    extraction_status TEXT NOT NULL,
    metadata_completeness NUMERIC(5,4) NOT NULL DEFAULT 0,
    evidence_quality TEXT NOT NULL DEFAULT 'UNKNOWN',
    freshness_status TEXT NOT NULL,
    extracted_text TEXT,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_mapping (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    evidence_document_id TEXT NOT NULL REFERENCES evidence_document(id),
    mapped_category TEXT NOT NULL,
    mapping_status TEXT NOT NULL,
    mapping_method TEXT NOT NULL,
    confidence NUMERIC(5,4) NOT NULL,
    review_note TEXT,
    mapped_to_metrics JSONB NOT NULL DEFAULT '[]'::jsonb,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_claim (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    evidence_document_id TEXT NOT NULL REFERENCES evidence_document(id),
    evidence_mapping_id TEXT NOT NULL REFERENCES evidence_mapping(id),
    claim_text TEXT NOT NULL,
    claim_tag TEXT NOT NULL,
    location_reference TEXT,
    quoted_snippet TEXT,
    used_for JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence TEXT NOT NULL,
    assumption_note TEXT,
    review_status TEXT NOT NULL DEFAULT 'PENDING',
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS metric_result (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    metric_code TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value NUMERIC(12,4) NOT NULL,
    unit TEXT NOT NULL,
    threshold_band TEXT,
    status TEXT NOT NULL,
    formula TEXT NOT NULL,
    confidence TEXT NOT NULL,
    error_margin TEXT NOT NULL,
    evidence_claim_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_gap_impact TEXT,
    rule_package_version TEXT NOT NULL,
    engine_run_id TEXT NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS engine_run (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    rule_package_version TEXT NOT NULL,
    evidence_index_version TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    mode TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_artifact (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    report_type TEXT NOT NULL,
    file_format TEXT NOT NULL,
    artifact_uri TEXT NOT NULL,
    official_status TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    rule_package_version TEXT NOT NULL,
    evidence_index_version TEXT NOT NULL,
    verification_id TEXT,
    content_hash TEXT NOT NULL,
    content TEXT NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_event (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    user_id TEXT,
    event_type TEXT NOT NULL,
    from_state TEXT,
    to_state TEXT,
    correlation_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS validation_alert (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    case_id TEXT NOT NULL REFERENCES assessment_case(id),
    severity TEXT NOT NULL,
    rule_code TEXT NOT NULL,
    message TEXT NOT NULL,
    required_action TEXT NOT NULL,
    triggered_metric_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'OPEN',
    payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assessment_case_tenant ON assessment_case(tenant_id);
CREATE INDEX IF NOT EXISTS idx_evidence_document_case ON evidence_document(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_case ON audit_event(case_id);

