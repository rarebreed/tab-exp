
import random
from typing import Literal, TypeAlias, TypedDict, cast

from mimesis import Field, Fieldset
from mimesis.enums import TimestampFormat
from mimesis.locales import Locale

field = Field(Locale.EN, seed=0xff)
fieldset = Fieldset(Locale.EN, seed=0xff)



class User(TypedDict):
    name: str
    address: str
    phone: str
    email: str

class Activity(TypedDict):
    start: int
    end: int


class Event(TypedDict):
    participant: User
    user_id: str
    contacts: list[User]
    organization_id: str
    business_unit: str
    resources: str
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
    return f"{field('address')}, {field('address.city')}, {field('address.state')} {field('address.zip_code')}"

def schema_gen() -> Event:
    start: int = field("timestamp", fmt=TimestampFormat.POSIX)
    end = start + random.randint(10, 3000)

    evt = cast(Event, {
        "participant": {
            "name": field("person.full_name"),
            "address": full_address(),
            "phone": field("person.telephone"),
            "email": field("email")
        },
        "user_id": field("uuid"),
        "contacts": fieldset("person.full_name", i=random.randint(0,4)),
        "organization_id": field("uuid"),
        "business_unit": field("choice", items=["HR", "Support", "Sales", "Manufacturing", "Engineering"]),
        "resources": fieldset("text.word"),
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



def textualize(event: Event):
    return f"""For event_id {event['event_id']}, the following information was collected.  The participant_name is 
    {event['participant']['name']}, the participant_address is {event['participant']['address']}, the participant_phone 
    number is {event['participant']['phone']}, and the participaint email address is {event['participant']['email']}.
    The user_id is {event['user_id']}, the business_unit is {event['business_unit']}, the priority is {event['priority']},
    the version is {event['version']}, and the anonymized value is {event['anonymized']}.  The organization id is 
    {event['organization_id']},
"""