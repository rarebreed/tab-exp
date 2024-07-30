# create a pytest unit test to test tab,schema_gen
import pytest
from tab_exp.tab import Event, anonymizer, is_anonymized, randomizer, event_generator, make_dataset


@pytest.fixture()
def event() -> Event:
    return event_generator()


def test_schema_gen(event: Event):
    assert isinstance(event, dict)  # Verify that the result is a dictionary
    assert "participant" in event  # Verify that the participant field exists
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
    assert anonymized_field is False, "event was not anonymized"
    # Verify that the event_id field is a string
    assert isinstance(event_id_field, str)


def test_random():
    evt1 = event_generator()
    evt2 = event_generator()
    print(evt1)
    print(evt2)
    assert evt1 != evt2, "events should have different values"


def test_text_orig(event: Event):
    doc = make_dataset(event, "orig")
    print(doc)
    assert isinstance(doc[0]["text"], str), "text feature should be a str"
    assert doc[0]["label"] == 0, "the label should be orig"


@pytest.fixture
def event_to_anonymize():
    return event_generator()  # Create an Event instance using the schema_gen function


def test_anonymizer(event_to_anonymize):
    anonymized_event = anonymizer(event_to_anonymize)

    for key in anonymized_event['participant'].keys():
        assert anonymized_event["participant"][key] != event_to_anonymize["participant"][key]
        atype = "uuid" if key == "user_id" else "random"
        assert is_anonymized(anonymized_event['participant'][key]) == atype
    for o_contact, a_contact in zip(event_to_anonymize["contacts"], anonymized_event["contacts"]):
        for key in a_contact.keys():
            assert o_contact[key] != a_contact[key]
    assert anonymized_event["organization_id"] != event_to_anonymize["organization_id"]

    # You can add more asserts as needed to validate other fields


@pytest.mark.parametrize("value,expected", [
    ("123e4567-e89b-12d3-a456-426655443131", "uuid"),
    ("not_a_uuid", "none"),
    ("another_not_uuid", "none"),
])
def test_is_anonymized(value, expected):
    assert is_anonymized(value) == expected


def test_randomizer():
    assert is_anonymized(randomizer()) == "random"

# Test that non-matching values are correctly identified as "none"


@pytest.mark.parametrize("value", [
    "hello world",
    "1234567890abcdef",
    " invalid uuid",
])
def test_non_matching_values(value):
    assert is_anonymized(value) == "none"

# Test that an empty string is correctly identified as "none"


def test_empty_string():
    assert is_anonymized("") == "none"
