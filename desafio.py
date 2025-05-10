import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

def formatar_valor(valor):
    # valor em reais
    return f"R$ {valor:.2f}"

def validar_valor(valor_input):
    # somente numeros positivos
    valor_input = valor_input.replace('.', '').replace(',', '.')
    if valor_input.isdigit() or (valor_input.replace('.', '', 1).isdigit() and valor_input.count('.') < 2):
        return float(valor_input)
    return None

# classe pai
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


# Pessoa herda de Cliente (filha)
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# Classe que representa uma conta bancária (pai)
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0  # Inicializa o saldo da conta como 0
        self._numero = numero  # Armazena o número da conta
        self._agencia = "0001"  # Define a agência da conta
        self._cliente = cliente  # Armazena o cliente associado à conta
        self._historico = Historico()  # Cria um objeto Historico para armazenar transações

    @classmethod
    def nova_conta(cls, cliente, numero):
        # Método de classe que cria uma nova conta
        return cls(numero, cliente)  # Retorna uma nova instância de Conta
    @property
    def saldo(self):
        return self._saldo  # Retorna o saldo da conta
    @property
    def numero(self):
        return self._numero  # Retorna o número da conta

    @property
    def agencia(self):
        return self._agencia  # Retorna a agência da conta
    @property
    def cliente(self):
        return self._cliente  # Retorna o cliente associado à conta

    @property
    def historico(self):
        return self._historico  # Retorna o histórico de transações da conta

    def sacar(self, valor_input):
        # Método para realizar um saque
        saldo = self.saldo  # Obtém o saldo atual da conta
        excedeu_saldo = valor_input > saldo  # Verifica se o valor do saque excede o saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")  # Mensagem de erro se o saldo for insuficiente
        elif valor_input is not None and valor_input > 0:
            self._saldo -= valor_input  # Deduz o valor do saldo
            print("\n=== Saque realizado com sucesso! ===")  # Mensagem de sucesso
            return True  # Retorna True indicando que o saque foi bem-sucedido
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")  # Mensagem de erro se o valor for inválido
        return False  # Retorna False indicando que o saque falhou

    def depositar(self, valor_input):
        # Método para realizar um depósito
        if valor_input is not None and valor_input > 0:
            self._saldo += valor_input  # Adiciona o valor ao saldo
            print("\n=== Depósito realizado com sucesso! ===")  # Mensagem de sucesso
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")    # Mensagem de erro
            return False

        return True

# classe ContaCorrente (filha de conta)
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor_input):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor_input > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor_input)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

# classe Historico
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

# classe Transacao (pai)
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


# classe Deposito (filha)
class Deposito(Transacao):
    def __init__(self, valor_input):
        self._valor = valor_input

    @property
    def valor_input(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor_input)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

# classe Saque (filha)
class Saque(Transacao):
    def __init__(self, valor_input):
        self._valor = validar_valor(valor_input)  # Use a função de validação

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# menu 
def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

# deposito
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    # valor formatado
    valor_input = input("Informe o valor do depósito: ")
    transacao = Deposito(valor_input)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# sacar
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    # testar se cliente
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor_input = input("Informe o valor do saque: ")
    transacao = Saque(valor_input)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# mostrar extrato no formato
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

# criar cliente
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    # testar se ja for cliente
    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

# criar conta
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    # se não for cliente
    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return
    
    # sendo cliente
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")

# listar contas
def listar_contas(contas):
    # iterar sobre contas
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

# logica do menu
def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
