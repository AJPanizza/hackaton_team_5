from pyspark.sql.types import DoubleType, IntegerType

from cgm_pipeline.schemas import (
    CGM_SILVER_SCHEMA,
    DEVICE_TELEMETRY_RAW_SCHEMA,
    PATIENT_FEATURES_GOLD_SCHEMA,
    PATIENTS_RAW_SCHEMA,
)


def test_device_telemetry_raw_schema_field_count() -> None:
    assert len(DEVICE_TELEMETRY_RAW_SCHEMA.fields) == 11


def test_patients_raw_schema_field_count() -> None:
    assert len(PATIENTS_RAW_SCHEMA.fields) == 14


def test_cgm_silver_schema_field_count() -> None:
    assert len(CGM_SILVER_SCHEMA.fields) == 17


def test_patient_features_gold_schema_field_count() -> None:
    assert len(PATIENT_FEATURES_GOLD_SCHEMA.fields) == 12


# --- Spot checks: DEVICE_TELEMETRY_RAW_SCHEMA ---


def test_device_telemetry_glucose_is_double() -> None:
    field = DEVICE_TELEMETRY_RAW_SCHEMA["glucose_mg_dl"]
    assert isinstance(field.dataType, DoubleType)


def test_device_telemetry_insulin_units_is_double() -> None:
    field = DEVICE_TELEMETRY_RAW_SCHEMA["insulin_units"]
    assert isinstance(field.dataType, DoubleType)


def test_device_telemetry_is_hypoglycemic_is_integer() -> None:
    field = DEVICE_TELEMETRY_RAW_SCHEMA["is_hypoglycemic"]
    assert isinstance(field.dataType, IntegerType)


def test_device_telemetry_alert_triggered_is_integer() -> None:
    field = DEVICE_TELEMETRY_RAW_SCHEMA["alert_triggered"]
    assert isinstance(field.dataType, IntegerType)


def test_device_telemetry_variability_cv_is_double() -> None:
    field = DEVICE_TELEMETRY_RAW_SCHEMA["variability_cv"]
    assert isinstance(field.dataType, DoubleType)


# --- Spot checks: PATIENTS_RAW_SCHEMA ---


def test_patients_age_is_integer() -> None:
    field = PATIENTS_RAW_SCHEMA["age"]
    assert isinstance(field.dataType, IntegerType)


def test_patients_has_cgm_is_integer() -> None:
    field = PATIENTS_RAW_SCHEMA["has_cgm"]
    assert isinstance(field.dataType, IntegerType)


# --- Spot checks: CGM_SILVER_SCHEMA ---


def test_silver_glucose_is_double() -> None:
    field = CGM_SILVER_SCHEMA["glucose_mg_dl"]
    assert isinstance(field.dataType, DoubleType)


def test_silver_age_is_integer() -> None:
    field = CGM_SILVER_SCHEMA["age"]
    assert isinstance(field.dataType, IntegerType)


def test_silver_has_cgm_is_integer() -> None:
    field = CGM_SILVER_SCHEMA["has_cgm"]
    assert isinstance(field.dataType, IntegerType)


# --- Spot checks: PATIENT_FEATURES_GOLD_SCHEMA ---


def test_gold_mean_glucose_is_double() -> None:
    field = PATIENT_FEATURES_GOLD_SCHEMA["mean_glucose"]
    assert isinstance(field.dataType, DoubleType)


def test_gold_std_glucose_is_double() -> None:
    field = PATIENT_FEATURES_GOLD_SCHEMA["std_glucose"]
    assert isinstance(field.dataType, DoubleType)


def test_gold_hypo_event_count_is_integer() -> None:
    field = PATIENT_FEATURES_GOLD_SCHEMA["hypo_event_count"]
    assert isinstance(field.dataType, IntegerType)


def test_gold_hyper_event_count_is_integer() -> None:
    field = PATIENT_FEATURES_GOLD_SCHEMA["hyper_event_count"]
    assert isinstance(field.dataType, IntegerType)


def test_gold_wear_time_ratio_is_double() -> None:
    field = PATIENT_FEATURES_GOLD_SCHEMA["wear_time_ratio"]
    assert isinstance(field.dataType, DoubleType)
