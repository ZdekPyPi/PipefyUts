#TEST FILE
from dotenv import load_dotenv
import sys
sys.path.append("./pipefyUts")
from pipefyUts import Pipefy,NewCard,CardField
import os

load_dotenv()
ORG_ID =  os.getenv("ORG_ID")
TOKEN  = os.getenv("TOKEN")

pfy = Pipefy(ORG_ID,TOKEN)


class DefaultCardInfo(NewCard):
    #DEFAULT
    __title__                = "reembolso_compradores"
    __pipeid__               = "1025104"

    #PIPEFY FIELDS
    tipo_de_solicita_o              = CardField(str,default="Solicitação")
    solicitante1                    = CardField(list,default=["401961749"])
    categoria                       = CardField(str,default="Comprador/Pedido")
    explique_o_que_voc_precisa      = CardField(str,default="Solicitação de Reembolso aberta para pedidos > 180 dias.")
    cnpj                            = CardField(str,default="null")
    n_do_evento_obrigat_rio         = CardField(str)
    tipo_de_conta                   = CardField(str)
    nome_da_pessoa_titular_da_conta = CardField(str)
    banco                           = CardField(str)
    c_digo_do_banco_n_o_obrigat_rio = CardField(str)
    ag_ncia_sem_digito_obrigat_rio  = CardField(str)
    conta_sem_digito_obrigat_rio    = CardField(str)
    digito_da_conta_obrigat_rio     = CardField(str)


class PerdaFinanceiraCard(DefaultCardInfo):

    #PIPEFY FIELDS
    solicita_o_comprador_pedido            = CardField(str,default="Perda Financeira Plataforma")
    teste_quem_o_respons_vel_pela_perda    = CardField(str,default="Sympla - Cobranças")
    por_que_a_sympla_deve_absorver_a_perda = CardField(str,default="Organizador devendo valor a Sympla")
    como_o_reembolso_deve_acontecer        = CardField(str,default="Transferência bancária ")  #NAO RETIRAR O ESPAÇO
    cpf_ou_cnpj_apenas_n_meros             = CardField(str,default="null")
    copy_of_valor_do_reembolso_obrigat_rio = CardField(float)
    n_do_pedido_obrigat_rio                = CardField(str)


    def __init__(self,**kwargs):
        pass

class Dias180Card(DefaultCardInfo):

    #PIPEFY FIELDS
    solicita_o_comprador_pedido     = CardField(str,default="Reembolso > 180 dias")
    cpf                             = CardField(str,default="null")
    valor_do_reembolso_obrigat_rio  = CardField(float)
    copy_of_n_do_pedido_obrigat_rio = CardField(str)


    #def __init__(self,**kwargs): NewCard.__init__(self,**kwargs)

myNewCard = PerdaFinanceiraCard(
    n_do_evento_obrigat_rio                = "2310947",
    tipo_de_conta                          = "Conta-corrente",
    nome_da_pessoa_titular_da_conta        = "Hannalice Gottschalck Cavalcanti",
    #cnpj                                   = "",
    cpf_ou_cnpj_apenas_n_meros             = "46629599420",
    banco                                  = "Banco do Brasil",
    c_digo_do_banco_n_o_obrigat_rio        = "1",
    ag_ncia_sem_digito_obrigat_rio         = "3525",
    conta_sem_digito_obrigat_rio           = "16276",
    digito_da_conta_obrigat_rio            = "0",
    copy_of_valor_do_reembolso_obrigat_rio = 80,
    n_do_pedido_obrigat_rio                = "26GP37091SR"
)

# myNewCard = Dias180Card(
#     n_do_evento_obrigat_rio         = "2310947",
#     tipo_de_conta                   = "Conta-corrente",
#     nome_da_pessoa_titular_da_conta = "Hannalice Gottschalck Cavalcanti",
#     banco                           = "Banco do Brasil",
#     c_digo_do_banco_n_o_obrigat_rio = "1",
#     ag_ncia_sem_digito_obrigat_rio  = "3525",
#     conta_sem_digito_obrigat_rio    = "16276",
#     digito_da_conta_obrigat_rio     = "0",
#     #cnpj                           = "",
#     cpf                             = "46629599420",
#     valor_do_reembolso_obrigat_rio  = 123.456,
#     copy_of_n_do_pedido_obrigat_rio = "123456"
# )



cd_id = pfy.createCard(card=myNewCard)


pfy.deleteCard(cd_id.get("id"))



pfy.listMembers()

pfy.listStartFormFields(pipe_id="1025104")

pfy.listCardsFromPhase(phase_id="325918208")



class MyCard(NewCard):
    #DEFAULT
    __title__                = "MyCardTitle"
    __pipeid__               = "304282374"

    #PIPEFY FIELDS
    descricao                = CardField(str,default="Teste")
    valor_total              = CardField(float)
    respons_vel_pela_an_lise = CardField(list)
    arquivos                 = CardField(list,is_file_path=True)

    def __init__(self,**kwargs): NewCard.__init__(self,**kwargs)


myNewCard = MyCard(
    # descricao                = "Teste",
    valor_total              = 1234567.89,
    respons_vel_pela_an_lise = ["301975616"],
    arquivos                 = [r"C:\Users\melque\Documents\Doc1.pdf"]
)

pfy.createCard(card=myNewCard)


pass

