# def create_chat(event: Event):
#     messages = [
#         {"role": "system",
#          "content": "You are a bot that responds to questions about Personally Identifiable Information (PII)."},
#         {"role": "user",
#          "content": f"Given the following JSON document:\n{event}\n, which fields in the JSON are PII?"},
#         {"role": "assistant",
#          "content": ""
#         }
#     ]
#     return messages

# def create_pii_field():
#     messages = [
#         {"role": "system",
#          "content": "You are a bot that responds to questions about Personally Identifiable Information (PII)"},
#         {"role": "user",
#          "content": "Is a JSON object that has a key name that ends in '_id' a PII field?"},
#         {"role":"assistant",
#          "content": "It depends.  If the value of the key is a unique identifier, then it is likely that it is PII, " +
#          "because it can be used to uniquely identify an individual.  If the value is not a unique identifier, then " +
#          "may be a coincidence that the key ends in '_id"},
#         {"role": "user",
#          "content": "If a key name in a JSON object ends in '_id', and the value is a unique value like a UUID, is " +
#          "the field a PII field?"},
#         {"role": "assistant",
#          "content": "Yes, it is more likely that the field is a PII, if the key starts with an entity related to a " +
#          "person.  For example, user_id is an example of a key in a JSON object that is PII.  However, if the start " +
#          "of the key is not related to a person, or to an external context related to a person, then it probably is " +
#          "not.  For example, event_id, bug_id, or process_id, would not be related to a person.  Keys like contact_id" +
#          "external_id, external_contact_id, are also most likely"}
#     ]
#     return messages
