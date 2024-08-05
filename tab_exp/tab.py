
from copy import deepcopy
import json
from pathlib import Path
from pprint import pprint
import random
import re
import shutil
import time
from typing import Literal, TypeAlias, TypedDict, cast

from mimesis import Field, Fieldset
from mimesis.enums import TimestampFormat
from mimesis.locales import Locale
import typer

PIILabel: TypeAlias = Literal["anon", "orig"]
PIILabelInt: TypeAlias = Literal[0, 1]

LabelMap: dict[str, PIILabelInt] = {
    "orig": 0,
    "anon": 1
}


class User(TypedDict):
    name: str
    address: str
    phone: str
    email: str
    user_id: str


class Activity(TypedDict):
    start: int
    end: int


class Event(TypedDict):
    participant: User
    user_id: str
    contacts: list[User]
    organization_id: str
    business_unit: str
    resources: list[str]
    activity: Activity
    channel: str
    priority: int
    version: int
    anonymized: bool
    event_id: str


def full_address():
    field = Field(Locale.EN, seed=random.randint(0, 255))
    return f"{field('address')}, {field('address.city')}, {field('address.state')} {field('address.zip_code')}"


def event_generator() -> Event:
    """Generate a random Event.

    This function uses the mimesis library to generate a fake event with various attributes,
    including participant, contacts, organization_id, business_unit, resources, activity,
    channel, priority, version, anonymized, and event_id.

    Returns:
        Event: A randomly generated event.
    """
    seed = random.randint(0, 255)
    field = Field(Locale.EN, seed=seed)
    fieldset = Fieldset(Locale.EN, seed=seed)

    start: int = field("timestamp", fmt=TimestampFormat.POSIX)
    end = start + random.randint(10, 3000)

    def make_user() -> User:
        return {
            "name": field("person.full_name"),
            "address": full_address(),
            "phone": field("person.telephone"),
            "email": field("email"),
            "user_id": field("uuid"),
        }

    evt = cast(Event, {
        "participant": make_user(),
        "contacts": [make_user() for _ in range(random.randint(1, 4))],
        "organization_id": field("uuid"),
        "business_unit": field("choice", items=["HR", "Support", "Sales", "Manufacturing", "Engineering"]),
        "resources": fieldset("text.word", i=random.randint(1, 5)),
        "activity": {
            "start": start,
            "end": end
        },
        "channel": field("choice", items=["chat", "call", "msg", "email"]),
        "priority": field("choice", items=[1, 2, 3, 4]),
        "version": field("choice", items=[1, 2, 3, 4]),
        "anonymized": False,
        "event_id": field("uuid")
    })
    return evt


def randomizer(values: int = 64) -> str:
    """Generate a hexadecimal string of the given length.

    This function generates a hexadecimal string with the specified number of values.
    Each value is randomly chosen from 0 to 15.

    Args:
        values (int): The desired length of the generated hexadecimal string.

    Returns:
        str: A random hexadecimal string.
    """
    return "".join(map(lambda _: f"{random.randint(0,15):x}", range(values)))


def is_anonymized(value: str, length: int = 64) -> Literal["uuid", "random", "none"]:
    """Determines the anonymization status of a given value.

    This function checks if the given value is a UUID or a randomly generated string. If it matches
    either pattern, it returns "uuid" or "random", respectively. Otherwise, it returns "none".

    Parameters:
        value (str): The value to check.
        length (int): The length of the random string pattern. Default is 64.

    Returns:
        Literal["uuid", "random", "none"]: The anonymization status of the given value.
    """
    rand_patt = re.compile(rf"^[a-f0-9]{{{length}}}$")
    uuid_patt = re.compile(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")

    m = rand_patt.search(value)
    if m:
        return "random"
    m = uuid_patt.search(value)
    if m:
        return "uuid"
    else:
        return "none"


def anonymizer(event: Event) -> Event:
    """Anonymizes an event by replacing sensitive information with randomly generated values.

    This function takes an event as input and returns a new event where the participant's information,
    contacts, organization ID, and other fields have been anonymized. The anonymization process
    replaces the original values with random strings or UUIDs to protect the identity of the
    individuals involved in the event.

    Parameters:
        event: The event to be anonymized

    Returns:
        A new event with anonymized information
    """
    field = Field(Locale.EN, seed=random.randint(0, 255))
    # make a deepcopy of the event
    event_cp = deepcopy(event)

    # anonymize the participant
    for key, _ in event_cp["participant"].items():
        if key == "user_id":
            event_cp["participant"]["user_id"] = field("uuid")
        else:
            event_cp["participant"][key] = randomizer()

    # anonymize the contacts
    for user in event_cp["contacts"]:
        for key, _ in user.items():
            if key == "user_id":
                user["user_id"] = field("uuid")
            else:
                user[key] = randomizer()

    # anonymize the organization_id
    event_cp["organization_id"] = field("uuid")
    event_cp["anonymized"] = True
    return event_cp


def ordinal(n: int) -> str:
    "returns the ordinal value of an int"
    if n == 1:
        return f"{n}st"
    elif n == 2:
        return f"{n}nd"
    elif n == 3:
        return f"{n}rd"
    else:
        return f"{n}th"


def user_str(users: list[User], name: str) -> list[str]:
    """
    This function takes a list of users and a name as input, then constructs
    a string that describes each user's attributes.

    Parameters: 
    users (list[User]): A list of User objects
    name (str): The name to use in the description

    Returns: str
    """
    builder: list[str] = []
    for i, user in enumerate(users, start=1):
        for key, value in user.items():
            if len(users) == 1:
                user_ord = ""
            else:
                user_ord = f"{ordinal(i)} "
            builder.append(f"The {user_ord}{name}_{key} is {value}.")
    return builder


def resource_str(resources: list[str]):
    return f"The resources are {','.join(resources)}.\n"


class PIIData(TypedDict):
    label: PIILabelInt
    text: str


def make_dataset(event: Event, label: PIILabel) -> list[PIIData]:
    participants = [(label, us)
                    for us in user_str([event["participant"]], "participant")]
    contacts = [(label, us) for us in user_str(event["contacts"], "contact")]
    data: list[PIIData] = [
        {"label": LabelMap[lbl], "text": line}
        for lbl, line in [
            *participants,
            *contacts,
            (label, f"The organization_id is {event['organization_id']}."),
            ("orig", f"The business_unit is {event['business_unit']}."),
            ("orig", resource_str(event["resources"])),
            ("orig",
             f"The activity_start time was {event['activity']['start']}."),
            ("orig", f"The activity_end time was {event['activity']['end']}."),
            ("orig",
             f"The channel used to contact the participant is {event['channel']}."),
            ("orig", f"The priority of the event is {event['priority']}."),
            ("orig", f"The version of the event is {event['version']}.")
        ]
    ]
    random.shuffle(data)
    return data


def jsonl(data: list[PIIData]) -> str:
    return "\n".join(json.dumps(d) for d in data)


class SynthDataPath(TypedDict):
    not_anonymized_path: str
    anonymized_path: str
    combined_path: str


def generate_synth_data(
    samples: int,
    output: str = "/tmp/synth_data",
    clean: bool = False,
    debug: bool = False
) -> SynthDataPath:
    start = time.time_ns()
    op = Path(output)
    if not op.exists():
        op.mkdir(parents=True)
    op_not_anon = op / "not_anonymized"
    op_anon = op / "anonymized"
    op_combined = op / "combined"
    if clean and op_not_anon.exists():
        shutil.rmtree(op_not_anon)
    if clean and op_anon.exists():
        shutil.rmtree(op_anon)
    if clean and op_combined.exists():
        shutil.rmtree(op_combined)
    op_not_anon.mkdir(exist_ok=True)
    op_anon.mkdir(exist_ok=True)
    op_combined.mkdir(exist_ok=True)

    gen = (event_generator() for _ in range(samples))
    all_orig_events: list[PIIData] = []
    all_anon_events: list[PIIData] = []
    for evt in gen:
        orig_events = make_dataset(evt, "orig")
        anon_events = make_dataset(anonymizer(evt), "anon")
        all_orig_events += orig_events
        all_anon_events += anon_events

    # Shuffle the original and anonymized.  This will help the LLM learn instead of learning a sequence
    random.shuffle(all_orig_events)
    random.shuffle(all_anon_events)

    # Create a combined version
    combined: list[PIIData] = all_orig_events + all_anon_events
    random.shuffle(combined)

    not_anon_jsonl = op_not_anon / "not_anonymized.jsonl"
    with open(not_anon_jsonl, "w+") as jf:
        jf.write(jsonl(all_orig_events))
    anon_jsonl = op_anon / "anonymized.jsonl"
    with open(anon_jsonl, "w+") as jf:
        jf.write(jsonl(all_anon_events))
    combined_jsonl = op_combined / "combined.jsonl"
    with open(combined_jsonl, "w+") as cf:
        cf.write(jsonl(combined))

    if debug:
        pprint(all_orig_events)
        print("======================")
        pprint(all_anon_events)
        not_anon_json = op_not_anon / "not_anonymized.json"
        with open(not_anon_json, "w") as not_anonymized_file:
            not_anonymized_file.write(json.dumps(all_orig_events, indent=2))
        anon_json = op_anon / "anonymized.json"
        with open(anon_json, "w") as anonymized_file:
            anonymized_file.write(json.dumps(all_anon_events, indent=2))

    end = time.time_ns()
    delta = (end - start) / 10**9
    print(f"{samples} events generated in {delta:.2f} seconds")
    print(f"averaged {(samples / delta):.2f} events/sec")
    return {
        "not_anonymized_path": str(not_anon_jsonl),
        "anonymized_path": str(anon_jsonl),
        "combined_path": str(combined_jsonl)
    }


if __name__ == "__main__":
    import typer
    typer.run(generate_synth_data)
