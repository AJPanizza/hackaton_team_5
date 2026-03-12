from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

DEVICE_TELEMETRY_RAW_SCHEMA = StructType(
    [
        StructField("reading_id", StringType(), nullable=False),
        StructField("patient_id", StringType(), nullable=False),
        StructField("device_type", StringType(), nullable=True),
        StructField("device_model", StringType(), nullable=True),
        StructField("reading_ts", TimestampType(), nullable=False),
        StructField("glucose_mg_dl", DoubleType(), nullable=True),
        StructField("insulin_units", DoubleType(), nullable=True),
        StructField("is_hypoglycemic", IntegerType(), nullable=True),
        StructField("is_hyperglycemic", IntegerType(), nullable=True),
        StructField("alert_triggered", IntegerType(), nullable=True),
        StructField("variability_cv", DoubleType(), nullable=True),
    ]
)

PATIENTS_RAW_SCHEMA = StructType(
    [
        StructField("patient_id", StringType(), nullable=False),
        StructField("full_name", StringType(), nullable=True),
        StructField("email", StringType(), nullable=True),
        StructField("phone", StringType(), nullable=True),
        StructField("address", StringType(), nullable=True),
        StructField("state", StringType(), nullable=True),
        StructField("zip_code", StringType(), nullable=True),
        StructField("age", IntegerType(), nullable=True),
        StructField("gender", StringType(), nullable=True),
        StructField("primary_condition", StringType(), nullable=True),
        StructField("insurance_type", StringType(), nullable=True),
        StructField("risk_tier", StringType(), nullable=True),
        StructField("has_cgm", IntegerType(), nullable=True),
        StructField("enroll_date", DateType(), nullable=True),
    ]
)

CGM_SILVER_SCHEMA = StructType(
    [
        StructField("patient_id", StringType(), nullable=False),
        StructField("reading_id", StringType(), nullable=False),
        StructField("device_type", StringType(), nullable=True),
        StructField("device_model", StringType(), nullable=True),
        StructField("reading_ts", TimestampType(), nullable=False),
        StructField("glucose_mg_dl", DoubleType(), nullable=True),
        StructField("insulin_units", DoubleType(), nullable=True),
        StructField("is_hypoglycemic", IntegerType(), nullable=True),
        StructField("is_hyperglycemic", IntegerType(), nullable=True),
        StructField("alert_triggered", IntegerType(), nullable=True),
        StructField("variability_cv", DoubleType(), nullable=True),
        StructField("age", IntegerType(), nullable=True),
        StructField("gender", StringType(), nullable=True),
        StructField("primary_condition", StringType(), nullable=True),
        StructField("risk_tier", StringType(), nullable=True),
        StructField("has_cgm", IntegerType(), nullable=True),
        StructField("_ingest_ts", TimestampType(), nullable=False),
    ]
)

PATIENT_FEATURES_GOLD_SCHEMA = StructType(
    [
        StructField("patient_id", StringType(), nullable=False),
        StructField("window_end", TimestampType(), nullable=False),
        StructField("mean_glucose", DoubleType(), nullable=True),
        StructField("std_glucose", DoubleType(), nullable=True),
        StructField("time_in_range_pct", DoubleType(), nullable=True),
        StructField("hypo_event_count", IntegerType(), nullable=True),
        StructField("hyper_event_count", IntegerType(), nullable=True),
        StructField("wear_time_ratio", DoubleType(), nullable=True),
        StructField("last_variability_cv", DoubleType(), nullable=True),
        StructField("risk_flag", StringType(), nullable=True),
        StructField("primary_condition", StringType(), nullable=True),
        StructField("risk_tier", StringType(), nullable=True),
    ]
)
