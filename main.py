from database import create_tables
from models import (
    ComandaJaAbertaError,
    ComandaNaoEncontradaError,
    ComandaService,
    formatar_moeda,
)


def ler_mesa():
    return input("Numero da mesa: ").strip()


def abrir_comanda(service):
    mesa = ler_mesa()
    comanda_id = service.abrir_comanda(mesa)
    print(f"Comanda {comanda_id} aberta para a mesa {mesa}.")


def adicionar_item(service):
    mesa = ler_mesa()
    nome = input("Nome do item: ").strip()
    preco = input("Preco do item: ").strip()
    item_id = service.adicionar_item(mesa, nome, preco)
    print(f"Item {item_id} adicionado com sucesso.")


def listar_itens(service):
    mesa = ler_mesa()
    itens = service.listar_itens(mesa)

    if not itens:
        print("A comanda ainda nao possui itens.")
        return

    print("\nItens da comanda:")
    for item in itens:
        print(f"{item['id']} - {item['nome']} - {formatar_moeda(item['preco_centavos'])}")


def mostrar_total(service):
    mesa = ler_mesa()
    total = service.calcular_total(mesa)
    print(f"Total da mesa {mesa}: {formatar_moeda(total)}")


def fechar_comanda(service):
    mesa = ler_mesa()
    total = service.fechar_comanda(mesa)
    print(f"Comanda da mesa {mesa} fechada. Total: {formatar_moeda(total)}")


def mostrar_menu():
    print(
        """
Sistema de Comandas
1 - Abrir comanda
2 - Adicionar item
3 - Listar itens da comanda
4 - Calcular total
5 - Fechar comanda
0 - Sair
"""
    )


def main():
    create_tables()
    service = ComandaService()
    opcoes = {
        "1": abrir_comanda,
        "2": adicionar_item,
        "3": listar_itens,
        "4": mostrar_total,
        "5": fechar_comanda,
    }

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "0":
            print("Encerrando o sistema.")
            break

        acao = opcoes.get(opcao)
        if not acao:
            print("Opcao invalida.")
            continue

        try:
            acao(service)
        except (ComandaJaAbertaError, ComandaNaoEncontradaError, ValueError) as exc:
            print(f"Erro: {exc}")


if __name__ == "__main__":
    main()
