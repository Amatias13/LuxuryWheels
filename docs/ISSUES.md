Lista de issues reportados — Luxury Wheels

O seguinte é a lista de problemas que encontro na aplicação (transcrito e organizada do pedido do utilizador):

1. O registo (Register) não mostra mensagem de sucesso — não há confirmação clara de criação de utilizador.
2. Não existe indicação clara de sessão iniciada — deve mostrar "Olá <Nome>" no canto superior (navbar).
3. Alguns textos estão em inglês e outros em português — traduzir toda a interface para português.
4. Existem textos com "Lorem ipsum" — substituir por conteúdo real.
5. Fichas de veículos não mostram "KM" nem "Model" e não indicam se o veículo está indisponível.
6. Navegação de datas: não é possível avançar/retroceder corretamente; não deve ser possível selecionar um `start` anterior a hoje nem um `end` anterior ao `start`.
7. Não deve ser possível aceder à página de reserva para um veículo indisponível (bloquear acesso/mostrar mensagem).
8. Aparece "NaN" no total estimado — cálculo de dias/preço falha quando datas não são válidas ou não parseadas.
9. Não consigo reservar um carro que está (supostamente) disponível — fluxo de reserva com falha/inconsistência.
10. Ao carregar em "Reservar" a página fica escura/preta — investigar overlay/modal/erro JS que causa esse comportamento.
11. Página "Contacte connosco" tem texto/markup incorreto — precisa revisão de conteúdo e layout.
12. "As minhas reservas" mostra mensagens de sucesso sem sentido — limpar mensagens irrelevantes e só mostrar feedback válido.
13. O footer não aparece corretamente na página "As minhas reservas" — problema de layout/partials.
14. Pareço perder sessão quando entro em "As minhas reservas" — investigar sessão/redirects e persistência de `session`.
15. Em locais a etiqueta mostra "Reserva" quando o rótulo correto seria "Procurar" (UX inconsistente).

Observações e sugestões rápidas
- Prioridade sugerida: 1) erros de autenticação/sessão (1,2,14), 2) cálculo e UX de reserva (6,8,9,10), 3) disponibilidade e exibição de veículos (5,7), 4) conteúdo/idioma (3,4,11,12,15), 5) layout footer (13).
- Ficheiro com schema e seeds: `database/scripts/createBD.SQLite` (usar para recriar BD de teste).
- Páginas e ficheiros a verificar inicialmente:
  - Registo/login: `routes/users.py`, `templates/register.html`, `templates/login.html`.
  - Navbar/session: `templates/partials/navbar.html` (ou onde estiver o navbar).
  - Reserva: `routes/reservations.py`, `templates/reservation.html`, `templates/edit_reservation.html`, `templates/my_reservations.html`.
  - JS responsável por datas e total: `templates/assets/js/main.js` (ou equivalente).
  - Contacto: `templates/contact.html`.

Próximo passo recomendado
- Validar item por item: reproduzir cada problema no ambiente local, anotar exactos passos para reproduzir e implementar correções em rama separada.
- Quer que eu comece a resolver um item específico agora? Se sim, indique o número(s) de prioridade (ex.: começar por 1,2 e 8).