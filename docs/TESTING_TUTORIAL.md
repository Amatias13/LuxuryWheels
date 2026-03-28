Tutorial de Testes — Luxury Wheels

Objetivo

- Verificar implementação dos requisitos da "Proposta A": registo/login, pesquisa, reserva com datas, escolha de pagamento, edição/cancelamento e regras de disponibilidade.

Pré-requisitos

- Python 3.10+ e ambiente virtual ativado no diretório do projeto.
- Dependências instaladas: `pip install -r requirements.txt`.
- Banco de dados: iremos usar o script `database/scripts/createBD.SQLite` para criar a BD SQLite.

1. Inicializar o projeto e BD

- Ativar venv (Windows PowerShell):

```powershell
& .\.venv\Scripts\Activate.ps1
```

- Instalar dependências (se necessário):

```powershell
pip install -r requirements.txt
```

- (Opcional) Regenerar o ficheiro SQLite a partir do script SQL:
  - Se tiver `sqlite3` instalado, execute:

```powershell
sqlite3 database/luxurywheels.db < database/scripts/createBD.SQLite
```

- Alternativamente, remova `database/luxurywheels.db` e deixe a app criar uma nova BD se o `app.py` suportar `init_db()` (verificar README do projeto).

2. Iniciar a aplicação

- Definir variáveis e arrancar o servidor Flask:

```powershell
$env:FLASK_APP = 'app.py'
$env:FLASK_ENV = 'development'
flask run
```

- Abrir no browser: `http://127.0.0.1:5000`

3. Registar e autenticar (Requisito 1)

- Ir para `Register` (ou `/register`).
- Preencher `firstName`, `lastName`, `email`, `password`, `re_password` e submeter.
- Depois do registo ir a `Login` (`/login`) e entrar com o email e password.
- Verificar: sessão criada (navbar mostra opções de utilizador), acesso a `/my-reservations` sem redirecionamento.

4. Pesquisar veículos (Requisito 2)

- Ir a página de listagem de veículos (`/cars` ou a rota principal onde está `car-list.html`).
- Usar a caixa de pesquisa para procurar por `model` ou `marca` (ex.: "M3", "Mercedes").
- Testar filtros:
  - Categoria (`category_filter`) — seleccionar uma categoria e aplicar.
  - Tipo do veículo (`type_filter`) — seleccionar um tipo e aplicar.
  - Valor da diária (`max_price`) — definir um máximo (ex.: 200) e aplicar.
  - Quantidade de pessoas (`capacity_filter`) — definir (ex.: 4) e aplicar.
- Verificar os resultados combinando filtros + pesquisa.

5. Fazer uma reserva (Requisitos 3,4)

- Ir à página de reserva do veículo (ex.: clicar em "Reservar" num veículo ou `/reservation?vehicle_id=<id>`).
- Preencher `startDate` e `endDate` (use o datepicker). As datas podem ser no formato exibido, o JS deve enviar em ISO para o servidor.
- Seleccionar um `Método de Pagamento` (obrigatório) e, opcionalmente, selecionar `Extras`.
- Submeter o formulário.
- Verificar:
  - Uma mensagem de sucesso com o total.
  - A entrada aparece em `As minhas reservas` (`/my-reservations`).
  - A tabela `Reservation` tem um novo registo com `totalDays`, `totalPrice` correto.
  - A tabela `Reservation_Extras_Link` contém linhas ligadas à reserva (se selecionou extras).
  - O veículo fica com `isActive = 0` (verificar com DB ou UI: deve aparecer indisponível).

6. Confirmação de pagamento e estado da reserva

- O fluxo atual cria um `Payment` automaticamente no `reserve` (status `Concluído`) e altera a reserva para `Confirmada`.
- Verificar na BD: tabela `Payment` tem um registo com `idReservation`, `idPaymentMethod`, `amount` igual ao total.
- Verificar na BD: `Reservation.idReservationStatus == 2` (Confirmada).

7. Edição de reservas (Requisito 5)

- Ir a `/my-reservations`, seleccionar uma reserva `Pendente/Confirmada` e clicar em `Editar` (se a UI expuser esse link).
- Alterar apenas `startDate` e/ou `endDate` e submeter.
- Restrições implementadas:
  - Não é possível editar dentro das 24 horas anteriores ao início: se a reserva começa em menos de 24 horas, a alteração é rejeitada.
  - Ao alterar, o sistema verifica disponibilidade do veículo no novo intervalo, ignorando a própria reserva.
- Verificar:
  - Após alteração válida, `Reservation.totalDays` e `totalPrice` são recalculados.
  - Se tentar alterar para intervalo sobreposto com outra reserva existente, a operação será rejeitada.

8. Cancelamento de reserva

- No `/my-reservations` seleccionar cancelar.
- Regras:
  - Cancelamento não permitido dentro das 24 horas anteriores ao início.
  - Ao cancelar, `Reservation.idReservationStatus` passa para `3` (Cancelada) e `Vehicle.isActive` volta a `1`.
- Verificar no DB e UI.

9. Regras de indisponibilidade por revisão/legalização (Requisito 5)

- O método `Vehicle.is_available()` aplica:
  - `isActive == 0` → indisponível.
  - `nextRevisionDate < hoje` → indisponível.
  - `lastLegalizationDate < hoje - 1 ano` → indisponível.

- Testar manualmente (duas opções):
  a) Alterar a BD com SQLite para simular falha de legalização ou revisão:

```sql
-- tornar legalizacao antiga (>1 ano)
UPDATE Vehicle SET lastLegalizationDate = '2020-01-01' WHERE idVehicle = 1;
-- tornar proxima revisao no passado
UPDATE Vehicle SET nextRevisionDate = '2020-01-01' WHERE idVehicle = 2;
```

b) Ou usar `/api/vehicle/<id>` PUT se preferir a API: enviar JSON com as datas.

- Depois destas alterações, tentar reservar o veículo nesses intervalos deve falhar com mensagem de "Veículo não disponível".

10. Verificações finais (integridade dos dados)

- Confirmar que todas as entidades essenciais existem na BD: `Vehicle`, `User`, `Reservation`, `Payment_Method`.
- Verificar índices (opcional) executando `PRAGMA index_list('Vehicle')` no sqlite3.

11. Testes automáticos simples (opcional)

- Usar endpoints `/api` genéricos para criar/ler dados rapidamente. Ex.: POST `/api/user` para criar um utilizador via JSON (o modelo `User.create` exigirá password no payload).

SQL úteis para inspecionar durante testes (usar `sqlite3 database/luxurywheels.db`):

```sql
-- Listar reservas
SELECT * FROM Reservation ORDER BY createdAt DESC LIMIT 10;
-- Ver extras de uma reserva
SELECT * FROM Reservation_Extras_Link WHERE idReservation = 1;
-- Verificar pagamento
SELECT * FROM Payment WHERE idReservation = 1;
-- Verificar veículo
SELECT idVehicle, model, isActive, lastLegalizationDate, nextRevisionDate FROM Vehicle WHERE idVehicle = 1;
```

Notas e observações

- O sistema marca o veículo como `isActive = 0` no momento da criação da reserva (comportamento T4). Isso impede reservas concorrentes imediatamente após a criação; se preferir um comportamento de "hold temporário" ou permitir múltiplas reservas confirmadas para diferentes intervalos, teremos de ajustar essa lógica.
- As datas aceites pelo backend: `YYYY-MM-DD` (ISO) e `DD/MM/YYYY` (o código faz parse de ambos). O frontend converte para ISO ao submeter.
- Se testar um banco existente (produção), faça backup antes de aplicar alterações SQL.

Se deseja, eu posso:

- Gerar um ficheiro `docs/TESTING_TUTORIAL.md` (já criado aqui) com estes passos (posso adaptar idioma/estilo);
- Gerar scripts SQL de teste (ex.: criar utilizador de teste com password conhecido);
- Gerar um conjunto de comandos curl/Postman collection para automatizar os testes.

Próximo passo: quer que eu gere um script SQL para criar um utilizador de teste com password `Test1234!` e instruções para recriar a BD (arquivo `.db`) a partir do `createBD.SQLite`?
