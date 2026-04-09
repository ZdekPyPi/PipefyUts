import requests
import json
import os
import pathlib
from .card import *
from .models import *
from urllib.parse import unquote,urlparse


import urllib3
urllib3.disable_warnings()

class Pipefy:
    url          = "https://api.pipefy.com/graphql"
    __graph_folder__ = os.path.join(pathlib.Path(__file__).parent.resolve(),"graphql")
    
    def __init__(self,org_id,token):
        self.org_id = org_id
        self.token = token
        self.headers = {"Authorization":f"Bearer {token}",'Content-Type': 'application/json'}

    def runQuery(self,query:str)->dict:
        query = {"query": query}
        req = requests.post(self.url,headers=self.headers,data=json.dumps(query))
        #VERIFICA SE O REQUEST DEU ERRO
        if req.status_code != 200:
            raise Exception(req.text)
        data = req.json()

        if "errors" in data:
            raise Exception(data["errors"][0]["message"])
        return req.json()

    def presignedUrl(self,file_name:str)->str:
        query = open(os.path.join(self.__graph_folder__,"presignedUrl.gql"),'r').read()
        query = query.replace("$org_id$",self.org_id)
        query = query.replace("$file_name$",file_name)

        data = self.runQuery(query)
        
        return data["data"]["createPresignedUrl"]["url"]
    
    def createAttachment(self,file_path:str)->str:
        #pega nome do arquivo
        f_name = os.path.basename(file_path)
        
        #cria uma variavel assinada
        url = self.presignedUrl(f_name)

        #------------------- ENVIA ARQUIVO PARA A URL
        
        req = requests.put(url, verify=False,data=open(file_path, 'rb').read(),headers={'Content-Type': 'application/octet-stream'})
        if req.status_code != 200:
            raise Exception(req.text)


        return unquote(url.split("?")[0].replace("https://pipefy-prd-us-east-1.s3.amazonaws.com/",""))

    def getCard(self,card_id):

        query = open(os.path.join(self.__graph_folder__,"getCard.gql"),'r').read()
        query = query.replace("$card_id$",card_id)

        data = self.runQuery(query)
        card = data.get("data").get("card")
        card = Card(
            self,
            card["id"],
            card["title"],
            card["created_at"],
            User(id=card["createdBy"]["id"],name=card["createdBy"]["name"]),
            Phase(self,card["current_phase"]["id"],card["current_phase"]["name"]),
            card.get("due_date")
        )

        return card

    def getPhase(self,phase_id):

        query = open(os.path.join(self.__graph_folder__,"get_phase.gql"),'r').read()
        query = query.replace("$phase_id$",phase_id)

        data = self.runQuery(query)
        phase = data.get("data").get("phase")
        phase = Phase(self,phase["id"],phase["name"])

        return phase

    def getPipe(self,pipe_id):
        query = open(os.path.join(self.__graph_folder__,"get_pipe.gql"),'r').read()
        query = query.replace("$pipe_id$",pipe_id)

        data = self.runQuery(query)
        pipe = data.get("data").get("pipe")
        pipe = Pipe(self,pipe["id"],pipe["name"])

        return pipe

    def members(self):
        query = open(os.path.join(self.__graph_folder__,"listMembers.gql"),'r').read()
        query = query.replace("$org_id$",self.org_id)
        data = self.runQuery(query)["data"]["organizations"]
        if not data:
            return None
        data = data[0]["members"]

        return [x.get("user") for x in data]
        
    def createCard(self,card:NewCard):
        query = open(os.path.join(self.__graph_folder__,"createCard.gql"),'r').read()
        query = query.replace("$title$",card.__title__)
        query = query.replace("$pipe_id$",card.__pipeid__)

        fields = []
        for f in card.used_fields:
            if f[1].type in [str,int,float]:
                value = object.__getattribute__(card,f[0])
                fields.append(f'{{field_id:{json.dumps(f[0])},field_value:{json.dumps(value)} }}')
            if f[1].type == list:
                value = object.__getattribute__(card,f[0])
                if f[1].is_file_path:
                    values = []
                    for fl in value:
                        values.append(self.createAttachment(fl))
                    fields.append(f'{{field_id:{json.dumps(f[0])},field_value:{json.dumps(values)} }}')
                elif f[1].list_sub_type in [str,int,float]:
                    fields.append(f'{{field_id:{json.dumps(f[0])},field_value:{json.dumps(value)} }}')
        
        fields = "\n,".join(fields)
        query = query.replace("$fields$",fields)
        query = query.replace('"null"',"null")

        return self.runQuery(query)["data"]["createCard"]["card"]

    def downloadFile(self, file_path,destination):
        req = requests.get(file_path,headers=self.headers,stream=True,verify=False)

        #VERIFICA SE O REQUEST DEU ERRO
        if req.status_code != 200:
            raise Exception(req.text)
        
        file_name = urlparse(req.url).path.split("/")[-1]
        file_addr = os.path.join(destination, file_name)

        with open(file_addr, "wb") as file:
            for chunk in req.iter_content(1024):
                file.write(chunk)

        return file_addr

