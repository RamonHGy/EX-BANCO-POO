from abc import ABC, abstractmethod
from datetime import datetime
import textwrap
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def criar_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def mumero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico


    def sacar(self, valor):
        saldo = self.saldo
        saldo_excedido = valor > saldo
        if saldo_excedido:
            print('Operação falhou! Saldo insuficiente.')
        elif valor > 0:
            self._saldo -= valor
            print('Saque realizado com sucesso')
            return True
        else:
            print('Operação falhou! Valor informado é invalido!')
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('Valor depositado com sucesso!')
            return True

        else:
            print('Operação falhou! Valor digitado inválido')
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.numero = numero
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__])

        limite_excedido = valor > self.limite
        saque_excedido = numero_saques >= self.limite_saques

        if limite_excedido:
            print('Operação falhou! Limite de saque excedido.')
        elif saque_excedido:
            print('Operação falhou! limite diario de saque excedido.')
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f'''
                Agência: {self.agencia}
                C/C: {self.numero}
                Titular Conta: {self.cliente.nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            'tipo': transacao.__class__.__name__,
            'valor': transacao.valor,
            'data': datetime.now().strftime('%d-%m-%y %H:%M:%S')
        }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def linha(tam=42):
    return '=' * tam


def cabecalho(txt):
    print(linha())
    print(txt.center(42))
    print(linha())

def menu(lista):
    cabecalho('OPERAÇÕES BANCO')
    c = 1
    for item in lista:
        print(f'{c} - {item}')
        c += 1
    print(linha())
    opcao = int(input('Escolha uma opcao: '))
    return opcao

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('Cliente não possui conta no sistema')
        return
    return cliente.contas[0]




def depositar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print('Cliente não encontrado no sistema! ')
        return

    valor = float(input('Informe o valor do depósito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = (input('Informe o CPF do cliente: '))
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado no sistema!')
        return
    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado')
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cabecalho('EXTRATO')
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas movimentações na conta'
    else:
        for transacao in transacoes:
            extrato += f'\n{transacao["tipo"]}:R$ {transacao["valor"]:.2f}'
    print(extrato)
    print(f'\nSaldo: R$ {conta.saldo:.2f}')


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print('Já existe cliente com esse CPF!')
        return

    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ')

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print('Cliente criado com sucesso!')


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('Cliente não encontrado, fluxo de criação de conta encerrado!')
        return

    conta = ContaCorrente.criar_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('Conta criada com sucesso!')


def listar_contas(contas):
    for conta in contas:
        cabecalho('Lista de contas')
        print(textwrap.dedent(str(conta)))

def main():
    from time import sleep
    clientes = []
    contas = []
    while True:
        resposta = menu(
            ['Depositar', 'Sacar', 'Extrato', 'Cadastrar conta', 'Cadastrar cliente', 'listar contas', 'Sair'])
        if resposta == 1:
            cabecalho('DEPÓSITO')
            depositar(clientes)

        elif resposta == 2:
            cabecalho('SAQUE')
            sacar(clientes)
        elif resposta == 3:
            exibir_extrato(clientes)
        elif resposta == 4:
            cabecalho('Cadastro de conta')
            numero_conta = len(contas)+1
            criar_conta(numero_conta, clientes, contas)
        elif resposta == 5:
            cabecalho('Cadastro de cliente')
            criar_cliente(clientes)
        elif resposta == 6:
            listar_contas(contas)
        elif resposta == 7:
            cabecalho('\033[0;31mEncerrando o sistema!\033[m')
            break
        else:
            print('Operação inválida! Escolha uma operação válida.')
        sleep(1.2)

main()