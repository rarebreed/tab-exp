# create a pytest unit test to test tab,schema_gen
import pytest
from tab_exp.tab import Event, schema_gen, textualize


@pytest.fixture()
def event() -> Event:
    return schema_gen()


def test_schema_gen(event: Event):
    assert isinstance(event, dict)  # Verify that the result is a dictionary
    assert "participant" in event  # Verify that the participant field exists
    assert "user_id" in event  # Verify that the user_id field exists
    assert "contacts" in event  # Verify that the contacts field exists
    # Add more assertions as needed to verify the expected structure and values of the resulting dictionary


def test_start_and_end_fields(event: Event):
    start_field = event["activity"]["start"]
    end_field = event["activity"]["end"]
    # Verify that the start field is an integer
    assert isinstance(start_field, int)
    # Verify that the end field is an integer
    assert isinstance(end_field, int)
    # Verify that the start time is less than or equal to the end time
    assert start_field <= end_field


def test_business_unit_and_resources_fields(event: Event):
    business_unit_field = event["business_unit"]
    resources_field = event["resources"]
    # Verify that the business_unit field is a string
    assert isinstance(business_unit_field, str)
    # Verify that the resources field is a list
    assert isinstance(resources_field, list)


def test_anonymized_and_event_id_fields(event: Event):
    anonymized_field = event["anonymized"]
    event_id_field = event["event_id"]
    # Verify that the anonymized field is set to "false"
    assert anonymized_field == "false"
    # Verify that the event_id field is a string
    assert isinstance(event_id_field, str)


def test_text(event: Event):
    doc = textualize(event)
    print(doc)
