from dataclasses import dataclass
import pathlib
import os
from dateutil.parser import isoparse

graph_folder = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")

@dataclass
class User:
    id  : str
    name: str


class Comment:
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
        query = open(os.path.join(graph_folder,"deleteComment.gql"),'r').read()
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