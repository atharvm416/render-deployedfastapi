from sqlalchemy import (
    Table, Column, Integer, String, Numeric, ForeignKey, CheckConstraint, Text,
    TIMESTAMP, func
)
from database import metadata

vendor = Table(
    "vendor",
    metadata,
    Column("vendor_id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", Text),
    Column("vendor_type", String, nullable=False),
    Column("code", String, unique=True),
    Column("status", String),
    Column("email", String, nullable=False),
    Column("phone", String),
    Column("mobile_number", String),
    Column("website", String),
    Column("contact_name", String),
    Column("address1", String),
    Column("address2", String),
    Column("city", String),
    Column("state", String),
    Column("zip", String),
    Column("country", String),
    Column("tax_id", String),
    Column("compliance_status", String),
    Column("payment_terms", String),
    Column("discount_rate", Numeric),
    Column("credit_limit", Numeric),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("updated_at", TIMESTAMP, server_default=func.now(), onupdate=func.now()),

    CheckConstraint("discount_rate >= 0 AND discount_rate <= 100", name="check_discount_rate"),
    CheckConstraint("credit_limit >= 0", name="check_credit_limit"),
    CheckConstraint(
        "vendor_type IN ('service_provider', 'supplier', 'contractor', 'consultant', 'other')",
        name="check_vendor_type"
    ),
    CheckConstraint(
        "status IN ('active', 'inactive', 'pending_review', 'blacklisted')",
        name="check_vendor_status"
    ),
    CheckConstraint(
        "compliance_status IN ('compliant', 'pending_review', 'non_compliant', 'exempted')",
        name="check_compliance_status"
    ),
    CheckConstraint(
        "payment_terms IN ('net_30', 'net_60', 'net_90', 'immediate')",
        name="check_payment_terms"
    ),
)
