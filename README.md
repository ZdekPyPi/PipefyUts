# PipefyUts
#
### Installation

```sh
pip install pipefyUts
```

### Dependencies

This package requires the following dependencies:
- requests
- python-dateutil

These are automatically installed when you install pipefyUts via pip.

## GitHub
https://github.com/ZdekPyPi/PipefyUts


## Usage

<!-- //==================================================== -->
## Auth
##### python code
```py
from pipefyUts import Pipefy

ORG_ID =  "<your_org_id>"
TOKEN  = "<your_token>"

pfy = Pipefy(ORG_ID,TOKEN)

```

<!-- //==================================================== -->
## listMembers
```py

pfy.listMembers()

```
##### output
```json
[
    {"id":1,"name":"name_1","email":"email_1@email.com"},
    {"id":2,"name":"name_2","email":"email_2@email.com"},
    {"id":3,"name":"name_3","email":"email_3@email.com"},
    {"id":4,"name":"name_4","email":"email_4@email.com"}
]

```
<!-- //==================================================== -->
## listStartFormFields
```py

pfy.listStartFormFields(pipe_id="<pipe_id>")

```
##### output
```json
[
    {"id":"field_1","label":"field_label_1"},
    {"id":"field_2","label":"field_label_2"},
    {"id":"field_3","label":"field_label_3"},
    {"id":"field_4","label":"field_label_4"}
]
```

<!-- //==================================================== -->
## listCardsFromPhase
```py

pfy.listCardsFromPhase(phase_id="<phase_id>")

```
##### output
```json
[
    {"id":"card_id_1","fields":[{...},{...},{...},...]},
    {"id":"card_id_2","fields":[{...},{...},{...},...]},
    {"id":"card_id_3","fields":[{...},{...},{...},...]},
    {"id":"card_id_4","fields":[{...},{...},{...},...]}
]

```
<!-- //==================================================== -->
## createAttachment
```py

path = pfy.createAttachment(file_path="<my_file>")

```
##### output
```py
"orgs/123456-1234-1234-1234-123asd5as1ad5s1/uploads/123ad3-123ddas-123cs-123da-asdc21cas21/my_file.txt"

```



## cardCreation
### authentication first
```py
from pipefyUts import Pipefy,NewCard,CardField

ORG_ID =  "<your_org_id>"
TOKEN  = "<your_token>"

pfy = Pipefy(ORG_ID,TOKEN)

```
### create card schema
```py

class MyCard(NewCard):
    #DEFAULT
    __pipeid__               = "<my_pipe_id>"
    __title__                = "<card_title>"

    #PIPEFY FIELDS
    description              = CardField(str)
    total_ammount            = CardField(float)
    files                    = CardField(list)
    files                    = CardField(list,is_file_path=True)


```
### create card
```py
#CREATE CARD OBJECT
myNewCard = MyCard(
    description   = "AdtPro",
    total_ammount = 123.46,
    files         = ["<owner_id>"],
    files         = [r".\Doc1.pdf",r".\Doc2.txt"]
)

#RUN CARD CREATION
pfy.createCard(card=myNewCard)

```


##### output
```json
{"id":"card_id"}
```

## Card Manipulation

### Get a Card
```py
card = pfy.getCard(card_id="<card_id>")
```

### Move Card to Phase
```py
card.move(phase_id="<phase_id>")
```

### Delete Card
```py
card.delete()
```

### Get Card Fields
```py
fields = card.fields()
```
##### output
```json
{"field_id_1": "value1", "field_id_2": "value2", ...}
```

### Update Field Value
```py
card.updateFieldValue(field_id="<field_id>", value="<new_value>")
```

### Add Labels
```py
card.addLabels(label_ids=["<label_id1>", "<label_id2>"])
```

### Remove Labels
```py
card.removeLabels(label_ids=["<label_id1>", "<label_id2>"])
```

### Remove All Labels
```py
card.removeAllLabels()
```

### Get Comments
```py
comments = card.comments()
```

### Add Comment
```py
comment = card.newComment(text="<comment_text>")
```

### Get Labels
```py
labels = card.labels()
```