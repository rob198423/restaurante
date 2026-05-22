from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from database import get_connection


class ComandaNaoEncontradaError(Exception):
    """Indica que nao existe comanda aberta para a mesa informada."""


class ComandaJaAbertaError(Exception):
    """Indica que a mesa ja possui uma comanda aberta."""


def formatar_moeda(valor_centavos):
    reais = Decimal(valor_centavos) / Decimal(100)
    return f"R$ {reais:.2f}".replace(".", ",")


def preco_para_centavos(preco):
    try:
        valor = Decimal(str(preco).replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Preco invalido.") from exc

    if valor < 0:
        raise ValueError("O preco nao pode ser negativo.")

    centavos = (valor * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(centavos)


class ComandaService:
    def abrir_comanda(self, mesa):
        mesa = self._validar_mesa(mesa)

        if self.buscar_comanda_aberta(mesa):
            raise ComandaJaAbertaError(f"A mesa {mesa} ja possui uma comanda aberta.")

        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO comandas (mesa, status) VALUES (?, 'aberta')",
                (mesa,),
            )
            return cursor.lastrowid

    def adicionar_item(self, mesa, nome, preco):
        mesa = self._validar_mesa(mesa)
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome do item nao pode ficar em branco.")

        preco_centavos = preco_para_centavos(preco)
        comanda = self._obter_comanda_aberta_ou_falhar(mesa)

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO itens (comanda_id, nome, preco_centavos)
                VALUES (?, ?, ?)
                """,
                (comanda["id"], nome, preco_centavos),
            )
            return cursor.lastrowid

    def listar_itens(self, mesa):
        mesa = self._validar_mesa(mesa)
        comanda = self._obter_comanda_aberta_ou_falhar(mesa)

        with get_connection() as connection:
            itens = connection.execute(
                """
                SELECT id, nome, preco_centavos
                FROM itens
                WHERE comanda_id = ?
                ORDER BY id
                """,
                (comanda["id"],),
            ).fetchall()
        return [dict(item) for item in itens]

    def calcular_total(self, mesa):
        mesa = self._validar_mesa(mesa)
        comanda = self._obter_comanda_aberta_ou_falhar(mesa)

        with get_connection() as connection:
            total = connection.execute(
                "SELECT COALESCE(SUM(preco_centavos), 0) FROM itens WHERE comanda_id = ?",
                (comanda["id"],),
            ).fetchone()[0]
        return total

    def fechar_comanda(self, mesa):
        mesa = self._validar_mesa(mesa)
        comanda = self._obter_comanda_aberta_ou_falhar(mesa)
        total = self.calcular_total(mesa)

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE comandas
                SET status = 'fechada', fechada_em = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (comanda["id"],),
            )
        return total

    def buscar_comanda_aberta(self, mesa):
        mesa = self._validar_mesa(mesa)

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT id, mesa, status, criada_em
                FROM comandas
                WHERE mesa = ? AND status = 'aberta'
                """,
                (mesa,),
            ).fetchone()

    def _obter_comanda_aberta_ou_falhar(self, mesa):
        comanda = self.buscar_comanda_aberta(mesa)
        if not comanda:
            raise ComandaNaoEncontradaError(
                f"Nao existe comanda aberta para a mesa {mesa}."
            )
        return comanda

    @staticmethod
    def _validar_mesa(mesa):
        try:
            mesa = int(mesa)
        except (TypeError, ValueError) as exc:
            raise ValueError("O numero da mesa deve ser um inteiro.") from exc

        if mesa <= 0:
            raise ValueError("O numero da mesa deve ser maior que zero.")
        return mesa
