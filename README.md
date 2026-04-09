# PipefyUts

### Installation

```sh
pip install pipefyUts
```

### Dependencies

This package requires the following dependencies:
- requests
- python-dateutil

These are automatically installed when you install `pipefyUts` via pip.

## GitHub
https://github.com/ZdekPyPi/PipefyUts

## Usage

### Authentication

```py
from pipefyUts import Pipefy

ORG_ID = "<your_org_id>"
TOKEN = "<your_token>"

pfy = Pipefy(ORG_ID, TOKEN)
```

## Core methods

### List organization members

```py
members = pfy.members()
```

### Upload attachment

```py
attachment_path = pfy.createAttachment(file_path="path/to/file.txt")
```

### Download file

```py
downloaded = pfy.downloadFile(file_path="https://...", destination=".")
```

### Get a card

```py
card = pfy.getCard(card_id="<card_id>")
```

### Get a phase

```py
phase = pfy.getPhase(phase_id="<phase_id>")
```

### Get a pipe

```py
pipe = pfy.getPipe(pipe_id="<pipe_id>")
```

## Pipe operations

```py
pipe       = pfy.getPipe(pipe_id="<pipe_id>")
fields     = pipe.startFormFields()
cards      = pipe.cards()
find_cards = pipe.findCards(field_id="cnpj", field_value="12.123.123/1234-12")
phases     = pipe.phases()
labels     = pipe.labels()
```

## Phase operations

```py
phase = pfy.getPhase(phase_id="<phase_id>")
cards = phase.cards()
```

## Card manipulation

```py
card = pfy.getCard(card_id="<card_id>")
```

```py
card.move(phase_id="<phase_id>")
card.delete()
fields = card.fields()
card.updateFieldValue(field_id="<field_id>", value="<new_value>")
comments = card.comments()
comment  = card.newComment(text="<comment_text>")
labels   = card.labels()
card.addLabels(label_ids=["<label_id1>", "<label_id2>"])
card.removeLabels(label_ids=["<label_id1>", "<label_id2>"])
card.removeAllLabels()
card.refresh()
```

### Example: card fields output

```py
fields = card.fields()
```

```json
{"field_id_1": "value1", "field_id_2": "value2"}
```

## Create card using `NewCard`

```py
from pipefyUts import Pipefy, NewCard, CardField

ORG_ID = "<your_org_id>"
TOKEN = "<your_token>"

pfy = Pipefy(ORG_ID, TOKEN)

class MyCard(NewCard):
    __pipeid__ = "<my_pipe_id>"
    __title__ = "<card_title>"

    description = CardField(str)
    total_ammount = CardField(float)
    owners = CardField(list)
    files = CardField(list, is_file_path=True)

my_new_card = MyCard(
    description="AdtPro",
    total_ammount=123.46,
    owners=["<owner_id>"],
    files=[r".\Doc1.pdf", r".\Doc2.txt"]
)

created = pfy.createCard(card=my_new_card)
print(created)
```

##### Example output

```json
Card<My_Card_Title>
```

## `CardField` helpers

- `CardField(str)` for text fields
- `CardField(int)` for integer fields
- `CardField(float)` for numeric fields
- `CardField(list)` for list values
- `CardField(list, is_file_path=True)` for list of file paths to upload
