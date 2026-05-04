from __future__ import annotations
from dataclasses import dataclass
import pathlib
import os
import json
from dateutil.parser import isoparse
import requests
from urllib.parse import unquote, urlparse
from datetime import datetime



@dataclass
class User:
    id  : str
    name: str
    email: str = None

    def __repr__(self):
        return f'User<{self.name}>'


class Comment:
    __graph_folder__ = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    __pfy__ = None
    
    id          = None
    author_id   = None
    author_name = None
    created_at  = None
    text        = None

    __raw__ = None

    def __init__(self,pfy,id:str,author:User,created_at:str,text:str):
        self.__pfy__     = pfy
        self.id          = id
        self.author      = author
        self.created_at  = isoparse(created_at)
        self.text        = text
        pass

    def delete(self):
        query = open(os.path.join(self.__graph_folder__,"deleteComment.gql"),'r').read()
        query = query.replace("$comment_id$",self.id)
        self.__pfy__.runQuery(query)
        

    def __repr__(self):
        return f'Comment<{self.id}>'


class Label:
    __pfy__ = None

    id   = None
    name = None
    color = None

    def __init__(self,pfy,id:str,name:str,color:str):
        self.__pfy__ = pfy
        self.id      = id
        self.name    = name
        self.color   = color

    def __repr__(self):
        return f'Label<{self.name}>'

class Attachment:
    __pfy__ = None

    id   = None
    name = None
    url  = None

    def __init__(self,pfy,url:str):
        self.__pfy__ = pfy
        self.url     = url
    
    def download(self,path:str):
        req = requests.get(self.url,headers=self.__pfy__.headers,stream=True,verify=False)

        #VERIFICA SE O REQUEST DEU ERRO
        if req.status_code != 200:
            raise Exception(req.text)
        
        file_name = self.file_name
        file_addr = os.path.join(path, file_name)

        with open(file_addr, "wb") as file:
            for chunk in req.iter_content(1024):
                file.write(chunk)

        return file_addr
    
    @property
    def file_name(self):
        return urlparse(self.url).path.split("?")[0].split("/")[-1]

    def __repr__(self):
        return 'Attachment<{}>'.format(self.file_name)

class Card:
    __graph_folder__ = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    __pfy__ = None

    created_at = None
    created_by = None
    labels     = None
    due_date   = None
    phase      = None
    id         = None
    pipe       = None


    def __init__(self,pfy,pipe:Pipe,card_id:str,title:str,created_at:str,created_by:User,phase:Phase,due_date:str=None):
        self.__pfy__    = pfy
        self.pipe       = pipe
        self.id         = card_id
        self.title      = title
        self.created_at = isoparse(created_at)
        self.created_by = created_by
        self.phase      = phase
        self.due_date   = isoparse(due_date) if due_date else None

        pass
    
    #=============================================== CARD ACTIONS ===========================================

    def delete(self):
        query = f'mutation {{ N0 :deleteCard(input:{{id: "{self.id}"}}){{ clientMutationId }}}}'
        return self.__pfy__.runQuery(query)["data"]["N0"]["clientMutationId"]

    def move(self,phase_id:str):
        query = f'mutation {{moveCardToPhase(input: {{card_id: "{self.id}", destination_phase_id: "{phase_id}"}}){{card{{id}}}}}}'
        return self.__pfy__.runQuery(query)

    def format_field_value(self,field_data:dict):
        if not field_data["value"]: return None

        if field_data['field']['type'] == 'attachment':
            list_of_attachments = []
            for url in eval(field_data["value"]):
                list_of_attachments.append(Attachment(self.__pfy__,url))
            return list_of_attachments
        elif field_data['field']['type'] in [ 'assignee_select','label_select','connector','checklist_vertical','checklist_horizontal']:
            return eval(field_data["value"])
        elif field_data['field']['type'] == 'date':
            return datetime.strptime(field_data["value"], "%d/%m/%Y").date()
        elif field_data['field']['type'] == 'currency':
            return float(field_data["value"].replace(",",""))
        elif field_data['field']['type'] == 'due_date':
            return datetime.strptime(field_data["value"], "%d/%m/%Y %H:%M")
        elif field_data['field']['type'] == 'number':
            return float(field_data["value"])
        else:
            return field_data['value']


    #=============================================== FIELDS =================================================    
    def fields(self):
        query = open(os.path.join(self.__graph_folder__,"card_fields.gql"),'r').read()
        query = query.replace("$card_id$",self.id)

        data = self.__pfy__.runQuery(query)
        fields     = {x['field']['id']:self.format_field_value(x) for x in data["data"]["card"]["fields"]}
        return fields

    def start_fields(self):
        pipe_start_fields = self.pipe.startFormFields()
        all_fields = self.fields()

        return { k:v for k,v in all_fields.items() if k in [y['id'] for y in pipe_start_fields]     }



    def updateFieldValue(self,field_id:str,value):
        val = f'"{value}"' if isinstance(value,str) else value
        val = json.dumps(val) if isinstance(val,list) else val
        query = f'mutation {{updateFieldsValues(input: {{nodeId: "{self.id}", values: [{{fieldId: "{field_id}", value: {val}}}]}}){{success}}}}'
        return self.__pfy__.runQuery(query)
    
    def refresh(self):
        card = self.__pfy__.getCard(self.id)
        self.title      = card.title
        self.created_at = card.created_at
        self.created_by = card.created_by
        self.phase      = card.phase
        self.due_date   = card.due_date
        return self

    def fields_from_phase(self,phase_id:str):
        phase = self.__pfy__.getPhase(phase_id)
        return phase.fields_from_card(self)

    #================================================ COMMENTS ===============================================
    def comments(self):
        query = open(os.path.join(self.__graph_folder__,"card_comments.gql"),'r').read()
        query = query.replace("$card_id$",self.id)

        data = self.__pfy__.runQuery(query)
        raw_comments = data["data"]["card"]["comments"]
        comments = [Comment(self.__pfy__,x['id'],User(id=x['author']['id'],name=x['author']['name']),x['created_at'],x['text']) for x in raw_comments]
        return comments

    def newComment(self,text):
        query = open(os.path.join(self.__graph_folder__,"newComment.gql"),'r').read()
        query = query.replace("$card_id$",self.id)
        query = query.replace("$text$",text)

        data        = self.__pfy__.runQuery(query)
        raw_comment = data["data"]["createComment"]["comment"]
        comment     = Comment(self.__pfy__,raw_comment)
        return comment

    #================================================ LABELS =================================================

    def labels(self):
        query = open(os.path.join(self.__graph_folder__,"card_labels.gql"),'r').read()
        query = query.replace("$card_id$",self.id)

        data = self.__pfy__.runQuery(query)
        labels     = [Label(self.__pfy__,x['id'],x['name'],x['color']) for x in data["data"]["card"]["labels"]]
        return labels
    
    def addLabels(self,label_ids:list[int|str]):
        #AJUSTA FORMATOS
        label_ids = [str(x) for x in label_ids]

        #GET CURRENT LABELS
        current_labels = self.labels()
        final_labels = list(set([x.id for x in current_labels] + label_ids))

        query = open(os.path.join(self.__graph_folder__,"edit_card_labels.gql"),'r').read()
        query = query.replace("$card_id$",self.id)
        query = query.replace("$label_ids$",json.dumps(final_labels))

        data = self.__pfy__.runQuery(query)

        return "OK"

    def removeLabels(self,label_ids:list[int|str]):

        #AJUSTA FORMATOS
        label_ids = [str(x) for x in label_ids]
        #GET CURRENT LABELS
        current_labels = self.labels()
        final_labels = list(set([x.id for x in current_labels if x.id not in label_ids]))


        query = open(os.path.join(self.__graph_folder__,"edit_card_labels.gql"),'r').read()
        query = query.replace("$card_id$",self.id)
        query = query.replace("$label_ids$",json.dumps(final_labels))

        data = self.__pfy__.runQuery(query)

        return "OK"

    def removeAllLabels(self):

        query = open(os.path.join(self.__graph_folder__,"edit_card_labels.gql"),'r').read()
        query = query.replace("$card_id$",self.id)
        query = query.replace("$label_ids$","[]")

        data = self.__pfy__.runQuery(query)

        return "OK"


    def __repr__(self):
        return f'Card<{self.id}>'

    def attachments(self):
        fields = self.fields()
        attachments = []
        for field_id, value in fields.items():
            if isinstance(value,list) and len(value) > 0 and isinstance(value[0],Attachment):
                attachments += value
        return attachments




class Phase:
    __graph_folder__ = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    __pfy__ = None

    id   = None
    name = None

    def __init__(self,pfy,id:str,name:str):
        self.__pfy__ = pfy
        self.id      = id
        self.name    = name
    
    def __repr__(self):
        return f'Phase<{self.name}>'
    
    def formFields(self):
        query = open(os.path.join(self.__graph_folder__,"listPhaseFormFields.gql"),'r').read()
        query = query.replace("$phase_id$",self.id)

        data = self.__pfy__.runQuery(query)

        return data.get("data").get("phase").get("fields")
    
    def cards(self,nextPage=None):
        nextPage = f'"{nextPage}"' if nextPage else 'null'
        query = open(os.path.join(self.__graph_folder__,"listCardsFromPhase.gql"),'r').read()
        query = query.replace("$phase_id$",self.id)
        query = query.replace("$after$",nextPage)

        data = self.__pfy__.runQuery(query)
    
        cards = data["data"]["phase"]["cards"]
        next_page = cards["pageInfo"]["hasNextPage"]
        cards_filtered = [x.get("node") for x in cards["edges"]]
        cards_filtered = [
            Card(
                self.__pfy__,
                Pipe(self.__pfy__,card["pipe"]["id"],card["pipe"]["name"]),
                card["id"],
                card["title"],
                card["created_at"],
                User(id=card["createdBy"]["id"],name=card["createdBy"]["name"]),
                Phase(self.__pfy__,card["current_phase"]["id"],card["current_phase"]["name"]),
                card.get("due_date")
            ) 
            for card in cards_filtered
            ]
        if next_page:
            return cards_filtered+self.cards(nextPage=cards["pageInfo"]["endCursor"])
        
        return cards_filtered
    
    def fields_from_card(self,card: Card):
        my_fields = self.formFields()
        card_fields = card.fields()

        fields = {}
        for field in my_fields:
            if field['id'] in card_fields:
                fields[field['id']] = card_fields[field['id']]
        return fields


class Pipe:
    __graph_folder__ = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    __pfy__ = None

    id   = None
    name = None

    def __init__(self,pfy,id:str,name:str):
        self.__pfy__ = pfy
        self.id      = id
        self.name    = name
    
    def __repr__(self):
        return f'Pipe<{self.name}>'
    
    def startFormFields(self):
        query = open(os.path.join(self.__graph_folder__,"listStartFormFields.gql"),'r').read()
        query = query.replace("$pipe_id$",self.id)

        data = self.__pfy__.runQuery(query)

        return data.get("data").get("pipe").get("start_form_fields")
    
    def findCards(self,field_id:str,field_value:str):
        query = open(os.path.join(self.__graph_folder__,"findCards.gql"),'r').read()
        query = query.replace("$pipe_id$",self.id)
        query = query.replace("$field_id$",field_id)
        query = query.replace("$field_value$",field_value)

        data = self.__pfy__.runQuery(query)
        cards = data["data"]["findCards"]["edges"]

        cards_to_return = []
        for card in cards:
            card = card.get("node")
            cards_to_return.append(Card(
                self.__pfy__,
                Pipe(self.__pfy__,card["pipe"]["id"],card["pipe"]["name"]),
                card["id"],
                card["title"],
                card["created_at"],
                User(id=card["createdBy"]["id"],name=card["createdBy"]["name"]),
                Phase(self.__pfy__,card["current_phase"]["id"],card["current_phase"]["name"]),
                card.get("due_date")
            ))


        return cards_to_return

    def phases(self):
        query = open(os.path.join(self.__graph_folder__,"phases_from_pipe.gql"),'r').read()
        query = query.replace("$pipe_id$",self.id)

        data = self.__pfy__.runQuery(query)
        phases = data.get("data").get("pipe").get("phases")

        return [Phase(self.__pfy__,phase["id"],phase["name"]) for phase in phases]
    
    def labels(self):
        query = open(os.path.join(self.__graph_folder__,"listPipeLabels.gql"),'r').read()
        query = query.replace("$pipe_id$",self.id)

        data = self.__pfy__.runQuery(query)
        labels = [Label(self.__pfy__,x['id'],x['name'],x['color']) for x in data["data"]["pipe"]["labels"]]

        return labels