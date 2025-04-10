import pathlib
import os
from dateutil.parser import isoparse

graph_folder = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")

#========================= CREATE CARD =======================
class CardField:
    def __init__(self,type,is_file_path=False,list_sub_type=str,required=True,default=None) -> None:
        self.type         = type
        self.is_file_path = is_file_path
        self.list_sub_type= list_sub_type
        self.required     = required
        self.default      = default

    def validate_default(self):
        if self.default is None: return

        if self.type == str:
            if not isinstance(self.default,str):
                raise Exception("Invalid default value")
        if self.type == int:
            if not isinstance(self.default,int):
                raise Exception("Invalid default value")
        if self.type == float:
            if not (isinstance(self.default,float) or isinstance(self.default,int)) :
                raise Exception("Invalid default value")
        if self.type == list:
            if not isinstance(self.default,list):
                raise Exception("Invalid default value")
            for item in self.default:
                if item.__class__ not in [str,int,float]:
                    raise Exception(f"invalid default value  '{item}'")
                elif self.is_file_path and not os.path.isfile(item):
                    raise Exception(f"default file not found '{item}'")
                elif self.list_sub_type == str and not isinstance(item,str):
                    raise Exception(f"invalid default value '{item}'")
                elif self.list_sub_type == int and not isinstance(item,int):
                    raise Exception(f"invalid default value '{item}'")
                elif self.list_sub_type == float and not isinstance(item,float):
                    raise Exception(f"invalid default value '{item}'")


class NewCard:
    graph_folder = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    used_fields = None

    def __new__(cls,*args,**kwargs):
        instance = super(NewCard, cls).__new__(cls)
        #instance.__init__(**kwargs)
        # if isinstance(instance, Filho):
        #     print("Filho foi instanciado")
        instance.validateRequired(**kwargs)
        instance.validateFields(**kwargs)
        instance.setFields(**kwargs)
        return instance
        # pass

    # def __init__(self,**kwargs):
    #     self.validateRequired(**kwargs)
    #     self.validateFields(**kwargs)
    #     self.setFields(**kwargs)
    #     pass

    def setFields(self,**kwargs):
        
        for key, value in kwargs.items():
            setattr(self,key,value)
        
        #SET DEFAULT FIELDS
        my_fields = [(x,object.__getattribute__(self,x)) for x in self.__dir__() if isinstance(object.__getattribute__(self,x),CardField)]
        default_fields = [x for x in my_fields if x[1].default]

        not_defined = [x for x in default_fields if x[0] not in kwargs.keys()]

        for item in not_defined:
            setattr(self,item[0],item[1].default)

    def validateRequired(self,**kwargs):
        if not "__title__" in self.__dir__(): raise Exception("please define __title__")
        if not "__pipeid__" in self.__dir__(): raise Exception("please define __pipeid__")

        my_fields = [(x,object.__getattribute__(self,x)) for x in self.__dir__() if isinstance(object.__getattribute__(self,x),CardField)]
        required_ones = [x[0] for x in my_fields if x[1].required and x[1].default is None]
        missing = [x for x in required_ones if not x in kwargs]
        self.used_fields = [x for x in my_fields if x[1].required or x[1].default is not None]
        if missing: raise Exception(f"required field '{missing[0]}' not found!")


    def validateFields(self,**kwargs):
        my_fields = [x for x in self.__dir__()]
        for key, value in kwargs.items():
            if not key in my_fields:
                raise Exception(f"field '{key}' not found!")
            if not isinstance(object.__getattribute__(self,key),CardField):
                raise Exception(f"invalid field '{key}'")
            else:
                field = object.__getattribute__(self,key)
                if value.__class__ not in [str,int,list,float,int]:
                    raise Exception(f"invalid field type '{field.type}'")
                if field.type == str and not isinstance(value,str):
                    raise Exception(f"invalid value '{key}'")
                if field.type == float and not (isinstance(value,float) or isinstance(value,int)):
                    raise Exception(f"invalid value '{key}'")
                if field.type == int and not isinstance(value,int):
                    raise Exception(f"invalid value '{key}'")
                elif field.is_file_path and isinstance(value,str) and not os.path.isfile(value):
                    raise Exception(f"file not found '{value}'")
                elif field.type == list:
                    if not isinstance(value,list):
                        raise Exception(f"invalid field '{key}'")
                    for item in value:
                        if item.__class__ not in [str,int,list,float]:
                            raise Exception(f"invalid field type '{field.type}'")
                        elif field.is_file_path and not os.path.isfile(item):
                            raise Exception(f"file not found '{item}'")
                        elif field.list_sub_type == str and not isinstance(item,str):
                            raise Exception(f"invalid value '{item}'")
        pass





class Card:
    __pfy__ = None

    created_at = None
    created_by = None
    labels     = None
    due_date   = None
    id         = None
    fields     = None
    comments   = None

    __raw__ = None

    def __init__(self,pfy,dados:dict):
        self.__pfy__    = pfy
        self.__raw__    = dados.copy()
        self.id         = dados.pop('id')
        self.created_at = isoparse(dados.pop('created_at'))
        self.created_by = dados.pop('createdBy')
        self.due_date   = isoparse(dados.pop('due_date')) if dados['due_date'] else dados.pop('due_date')
        self.fields     = {x['field']['id']:x['value'] for x in dados.pop('fields')}
        self.comments   = [Comment(self.__pfy__,x) for x in dados.pop('comments')]
        self.labels     = dados.pop('labels')

        pass

    def newComment(self,text):
        query = open(os.path.join(graph_folder,"newComment.gql"),'r').read()
        query = query.replace("$card_id$",self.id)
        query = query.replace("$text$",text)

        data = self.__pfy__.runQuery(query)
        self.comments = [Comment(self.__pfy__,data["data"]["createComment"]["comment"])] + self.comments
        return self.comments[0]


        

    
    def __repr__(self):
        return f'Card<{self.id}>'


class Comment:
    __pfy__ = None
    
    id          = None
    author_id   = None
    author_name = None
    created_at  = None
    text        = None

    __raw__ = None

    def __init__(self,pfy,dados):
        self.__pfy__    = pfy
        self.__raw__    = dados
        self.id          = dados['id']
        self.author_id   = dados['author']['id']
        self.author_name = dados['author_name']
        self.created_at  = isoparse(dados['created_at'])
        self.text        = dados['text']
        pass

    def delete(self):
        query = open(os.path.join(graph_folder,"deleteComment.gql"),'r').read()
        query = query.replace("$comment_id$",self.id)
        self.__pfy__.runQuery(query)
        

    def __repr__(self):
        return f'Comment<{self.id}>'
