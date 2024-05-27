import pathlib
import os


#========================= CREATE CARD =======================
class CardField:
    def __init__(self,type,is_file_path=False,list_sub_type=str,required=True) -> None:
        self.type         = type
        self.is_file_path = is_file_path
        self.list_sub_type= list_sub_type
        self.required     = required


class NewCard:
    graph_folder = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    used_fields = None

    def __init__(self,**kwargs):
        self.validate_required(**kwargs)
        self.validate_fields(**kwargs)
        self.set_fields(**kwargs)

    def set_fields(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self,key,value)

    def validate_required(self,**kwargs):
        my_fields = [(x,object.__getattribute__(self,x)) for x in self.__dir__() if isinstance(object.__getattribute__(self,x),CardField)]
        required_ones = [x[0] for x in my_fields if x[1].required]
        missing = [x for x in required_ones if not x in kwargs]
        self.used_fields = [(x,object.__getattribute__(self,x)) for x in required_ones]
        if missing: raise Exception(f"required field '{missing[0]}' not found!")


    def validate_fields(self,**kwargs):
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

      