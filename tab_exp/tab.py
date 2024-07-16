
from copy import deepcopy
import random
import re
from typing import Literal, TypeAlias, TypedDict, cast

from mimesis import Field, Fieldset
from mimesis.enums import TimestampFormat
from mimesis.locales import Locale


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
    anonymized: Literal["false", "true"]
    event_id: str


PiiColumnName: TypeAlias = Literal[
    "participant.name",
    "participant.address",
    "participant.phone",
    "participant.email",
    "user_id",
    "contacts",
    "org_id",
]

ColumnName: TypeAlias = Literal[
    "business_unit",
    "resources",
    "activity.start",
    "activity.end",
    "channel",
    "priority",
    "media_type"
]

Column: TypeAlias = PiiColumnName | ColumnName

Columns = (
    "participant.name",
    "participant.address",
    "participant.phone",
    "participant.email",
    "user_id",
    "contacts",
    "org_id",
    "business_unit",
    "resources",
    "activity.start",
    "activity.end",
    "channel",
    "priority",
    "media_type",
    "version"
)


def full_address():
    field = Field(Locale.EN, seed=random.randint(0, 255))
    return f"{field('address')}, {field('address.city')}, {field('address.state')} {field('address.zip_code')}"


def schema_gen() -> Event:
    seed = random.randint(0, 255)
    field = Field(Locale.EN, seed=seed)
    fieldset = Fieldset(Locale.EN, seed=seed)

    start: int = field("timestamp", fmt=TimestampFormat.POSIX)
    end = start + random.randint(10, 3000)

    evt = cast(Event, {
        "participant": {
            "name": field("person.full_name"),
            "address": full_address(),
            "phone": field("person.telephone"),
            "email": field("email"),
            "user_id": field("uuid"),
        },
        "contacts": fieldset("person.full_name", i=random.randint(1, 4))[1:],
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
        "anonymized": "false",
        "event_id": field("uuid")
    })
    return evt


def randomizer(values: int = 64) -> str:
    return "".join(map(lambda _: f"{random.randint(0,15):x}", range(values)))


def is_anonymized(value: str, length: int = 64) -> Literal["uuid", "random", "none"]:
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
    return event_cp


def textualize(event: Event):
    d = [f"For event_id {event['event_id']}, the following information was collected.\n",
         f"The participant_name is {event['participant']['name']}, the participant_address is ",
         f"{event['participant']['address']}, the participant_phone is {event['participant']['phone']}, "
         f"and the participant_email is {event['participant']['email']}.\n",
         f"The user_id is {event['participant']['user_id']}, and the contacts are {event['contacts']}.\n",
         f"The organization_id is {event['organization_id']}, the business_unit is {event['business_unit']}, ",
         f"and the resources are {event['resources']}.\n",
         f"The activity_start time was {event['activity']['start']}, ",
         f"and the activity end time was {event['activity']['end']}.\n"
         f"The channel used to contact the participant was {event['channel']}, the priority of the event was ",
         f"{event['priority']}, and the version of the event was {event['version']}.\n"
         f"The anonymized field is {event['anonymized']}.\n"
         ]

    return ''.join(d)
