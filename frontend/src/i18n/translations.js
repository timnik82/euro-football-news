export const LANGUAGES = [
  { code: "en", label: "English", short: "EN" },
  { code: "ru", label: "Русский", short: "RU" },
  { code: "pt", label: "Português", short: "PT" },
];

export const DATE_LOCALES = { en: "en-GB", ru: "ru-RU", pt: "pt-PT" };

const translations = {
  en: {
    nav: { home: "Home", leagues: "Leagues", games: "Games", favorites: "Favorites", login: "Login", logout: "Logout", search: "Search" },
    home: {
      title: "Goal Kick!",
      comingUp: "Coming Up",
      todayMatches: "Today's Matches",
      seeAll: "See all",
      noMatches: "No matches right now",
      noMatchesSub: "Check back later or browse the leagues!",
      stories: "Match Stories",
      explore: "Explore Leagues",
    },
    league: {
      table: "Table",
      matches: "Matches",
      topScorers: "Top Scorers",
      upcoming: "Upcoming",
      recentResults: "Recent Results",
      noStandings: "Standings not available yet",
      noMatches: "No matches available",
      noScorers: "Top scorers not available for this competition",
      pts: "pts",
      ast: "ast",
      played: "P", won: "W", drawn: "D", lost: "L", gd: "GD", points: "Pts", team: "Team",
    },
    login: {
      welcomeBack: "Welcome Back!",
      joinClub: "Join the Club!",
      loginSub: "Log in to see your favorites",
      registerSub: "Create your account to save favorites",
      name: "Your Name",
      namePlaceholder: "e.g. Alex",
      email: "Email",
      emailPlaceholder: "your@email.com",
      password: "Password",
      passwordPlaceholder: "Your secret password",
      loginBtn: "Log In",
      registerBtn: "Create Account",
      toggleLogin: "Already have an account? Log in",
      toggleRegister: "New here? Create an account",
      skip: "Skip for now - browse matches",
    },
    favorites: {
      title: "My Favorites",
      leagues: "Leagues",
      teams: "Teams",
      empty: "No favorites yet",
      emptySub: "Browse leagues and tap the heart to save your favorite teams and competitions!",
      browseBtn: "Browse Leagues",
    },
    games: {
      title: "Games",
      subtitle: "Daily football challenge",
      refresh: "Refresh games",
      loadError: "Could not load the game right now",
      submitError: "Could not check your answer",
      dailyQuiz: "Daily quiz",
      crestQuiz: "Crest quiz",
      guessPlayer: "Guess the Player",
      guessCrest: "Guess the Crest",
      submit: "Lock in answer",
      checking: "Checking...",
      doneToday: "Done for today",
      correctToast: "Goal! Correct answer",
      tryTomorrow: "Nice try — new quiz tomorrow",
      alreadyPlayed: "You have already played today's quiz. Come back tomorrow for a fresh one!",
      scoreboard: "Scoreboard",
      points: "Points",
      streak: "Streak",
      correct: "Correct",
      badges: "Badges",
      achievements: "Achievements",
    },
    match: {
      live: "LIVE", ft: "FT", ht: "HT", today: "Today", tomorrow: "Tomorrow", matchday: "Matchday",
    },
    detail: {
      halfTime: "HT", timeline: "Match Timeline", firstHalf: "1st Half", secondHalf: "2nd Half",
      h2h: "Head to Head", meetings: "meetings", error: "Could not load match details",
      extraTime: "After Extra Time", penalties: "After Penalties",
      totalGoals: "goals in {n} meetings", winner: "Winner",
    },
    season: {
      matchday: "Matchday", of: "of", progress: "Season Progress",
    },
    team: {
      founded: "Founded", colors: "Colors", coach: "Coach", squad: "Squad", players: "players",
      yrs: "yrs", notFound: "Team not found",
      didYouKnow: {
        title: "Did you know?",
        founded: "{team} was founded in {year} — that is {age} years of football history!",
        venue: "Home matches are played at {venue}, the club's football home.",
        competition: "This season the team is playing in {competition}.",
        coach: "The coach is {coach}, the person planning training and tactics.",
        squad: "The squad has {count} players, so there are lots of lineup choices.",
        colors: "The club colours are {colors}; fans can spot them from far away.",
        fallbacks: [
          "Every crest tells a little story about {team}, its city, or its fans.",
          "Players usually train many times a week before match day.",
          "A loud home crowd can make a match feel extra exciting.",
        ],
      },
      pos: { goalkeeper: "Goalkeepers", defence: "Defenders", midfield: "Midfielders", offence: "Forwards" },
    },
    player: {
      club: "Club", nationality: "Nationality", age: "Age", born: "Born",
      number: "Number", contract: "Contract", notFound: "Player not found",
    },
    settings: { language: "Language", title: "Settings" },
    search: {
      placeholder: "Search teams & players...",
      teams: "Teams",
      players: "Players",
      noResults: "No results found",
      hint: "Type at least 2 characters to search",
    },
    offline: "You're offline - showing cached data",
    loading: "Loading...",
    loadingSub: "Getting the latest scores",
    nextMatch: {
      title: "Next match for your team",
      home: "Home",
      away: "Away",
      days: "Days",
      hours: "Hours",
      minutes: "Min",
      seconds: "Sec",
    },
    matchStory: {
      title: "Story of the Match",
      loading: "Finding the story behind this match…",
      fallback: "We could not find a full story for this match yet, but here is what we know from the match result.",
      fallbackBadge: "Result story",
      sources: "Sources",
      source: "Source",
      why: "Why it matters",
      watchHighlights: "Watch highlights",
      error: "We could not load the story right now. Try this match again later.",
    },
    story: {
      homeDominant: [
        "{home} storms past {away}!",
        "{home} powers clear of {away}!",
      ],
      awayDominant: [
        "{away} cruises past {home} away from home!",
        "{away} takes charge against {home} on the road!",
      ],
      homeControl: [
        "{home} takes a solid win over {away}.",
        "{home} gets the better of {away} with room to spare.",
      ],
      awayControl: [
        "{away} earns a solid away win against {home}.",
        "{away} handles {home} well on the road.",
      ],
      homeControlClean: [
        "{home} beats {away} and keeps it tidy at the back.",
        "{home} controls the game and shuts out {away}.",
      ],
      awayControlClean: [
        "{away} wins away at {home} without conceding.",
        "{away} stays sharp in defence and beats {home}.",
      ],
      homeNarrow: [
        "{home} just squeezes past {away}.",
        "{home} edges out {away} in a close one.",
      ],
      awayNarrow: [
        "{away} nips past {home} away from home.",
        "{away} edges {home} in a very close match.",
      ],
      homeNarrowClean: [
        "{home} grabs a slim win over {away}.",
        "{home} seals a narrow victory against {away}.",
      ],
      awayNarrowClean: [
        "{away} holds on for a narrow win at {home}.",
        "{away} takes a tight away victory over {home}.",
      ],
      drawNoGoals: [
        "{home} and {away} cancel each other out.",
        "No goals as {home} and {away} finish level.",
      ],
      drawEven: [
        "{home} and {away} share the points.",
        "{home} and {away} finish all square.",
      ],
      drawWild: [
        "{home} and {away} trade goals in a lively draw.",
        "Plenty happened as {home} and {away} draw {h}-{a}.",
      ],
      summaryDominant: [
        "{winner} had the game under control and won {h}-{a}.",
        "{winner} looked stronger for long spells and finished with a {h}-{a} win.",
      ],
      summaryDominantHighScoring: [
        "{winner} scored freely and wrapped up a big {h}-{a} win.",
        "With plenty of attacking power, {winner} pulled away to win {h}-{a}.",
      ],
      summaryDominantCleanSheet: [
        "{winner} kept a clean sheet and never really let {loser} settle.",
        "{winner} stayed firm at the back and finished off a clear {h}-{a} win.",
      ],
      summaryControl: [
        "{winner} found a bit more quality and earned a deserved {h}-{a} win.",
        "{winner} made the key moments count and took the match {h}-{a}.",
      ],
      summaryControlCleanSheet: [
        "{winner} stayed organised, kept things calm, and won {h}-{a}.",
        "A tidy defensive display helped {winner} secure a {h}-{a} victory.",
      ],
      summaryNarrow: [
        "It stayed close, but {winner} did enough to win {h}-{a}.",
        "There was little between the teams, yet {winner} just came out on top {h}-{a}.",
      ],
      summaryNarrowCleanSheet: [
        "{winner} protected the lead well and finished with a {h}-{a} win.",
        "A careful finish from {winner} was enough for a narrow {h}-{a} victory.",
      ],
      summaryDrawNoGoals: [
        "Neither side could find the breakthrough, so it ended 0-0.",
        "Chances were limited, and both teams had to settle for 0-0.",
      ],
      summaryDrawEven: [
        "Both teams had their moments, and the match ended {h}-{a}.",
        "It was a balanced game, and {home} and {away} finished level at {h}-{a}.",
      ],
      summaryDrawWild: [
        "Goals at both ends made this a fun {h}-{a} draw.",
        "It was lively from start to finish, ending in a {h}-{a} draw.",
      ],
    },
  },
  ru: {
    nav: { home: "Главная", leagues: "Лиги", games: "Игры", favorites: "Избранное", login: "Войти", logout: "Выход", search: "Поиск" },
    home: {
      title: "Goal Kick!",
      comingUp: "Ближайшие матчи",
      todayMatches: "Матчи сегодня",
      seeAll: "Все",
      noMatches: "Сейчас нет матчей",
      noMatchesSub: "Загляните позже или полистайте лиги!",
      stories: "Обзоры матчей",
      explore: "Все лиги",
    },
    league: {
      table: "Таблица",
      matches: "Матчи",
      topScorers: "Бомбардиры",
      upcoming: "Предстоящие",
      recentResults: "Последние результаты",
      noStandings: "Таблица пока недоступна",
      noMatches: "Матчей пока нет",
      noScorers: "Данные о бомбардирах недоступны",
      pts: "очк",
      ast: "пас",
      played: "И", won: "В", drawn: "Н", lost: "П", gd: "РМ", points: "Очки", team: "Команда",
    },
    login: {
      welcomeBack: "С возвращением!",
      joinClub: "Вступай в клуб!",
      loginSub: "Войди, чтобы видеть избранное",
      registerSub: "Создай аккаунт, чтобы сохранять любимые команды",
      name: "Твоё имя",
      namePlaceholder: "напр. Алекс",
      email: "Почта",
      emailPlaceholder: "твоя@почта.com",
      password: "Пароль",
      passwordPlaceholder: "Твой секретный пароль",
      loginBtn: "Войти",
      registerBtn: "Создать аккаунт",
      toggleLogin: "Уже есть аккаунт? Войти",
      toggleRegister: "Впервые здесь? Создать аккаунт",
      skip: "Пропустить - смотреть матчи",
    },
    favorites: {
      title: "Моё избранное",
      leagues: "Лиги",
      teams: "Команды",
      empty: "Пока пусто",
      emptySub: "Листай лиги и нажимай на сердечко, чтобы сохранить любимые команды!",
      browseBtn: "Смотреть лиги",
    },
    games: {
      title: "Игры",
      subtitle: "Ежедневный футбольный челлендж",
      refresh: "Обновить игры",
      loadError: "Не удалось загрузить игру прямо сейчас",
      submitError: "Не удалось проверить ответ",
      dailyQuiz: "Ежедневная викторина",
      crestQuiz: "Викторина по эмблемам",
      guessPlayer: "Угадай игрока",
      guessCrest: "Угадай эмблему",
      submit: "Ответить",
      checking: "Проверяем...",
      doneToday: "На сегодня всё",
      correctToast: "Гол! Ответ верный",
      tryTomorrow: "Хорошая попытка — завтра будет новая викторина",
      alreadyPlayed: "Сегодняшняя викторина уже сыграна. Возвращайся завтра за новой!",
      scoreboard: "Табло",
      points: "Очки",
      streak: "Серия",
      correct: "Верно",
      badges: "Бейджи",
      achievements: "Достижения",
    },
    match: {
      live: "LIVE", ft: "КМ", ht: "Перерыв", today: "Сегодня", tomorrow: "Завтра", matchday: "Тур",
    },
    detail: {
      halfTime: "Перерыв", timeline: "Ход матча", firstHalf: "1-й тайм", secondHalf: "2-й тайм",
      h2h: "Личные встречи", meetings: "встреч", error: "Не удалось загрузить данные матча",
      extraTime: "После доп. времени", penalties: "По пенальти",
      totalGoals: "голов в {n} встречах", winner: "Победитель",
    },
    season: {
      matchday: "Тур", of: "из", progress: "Прогресс сезона",
    },
    team: {
      founded: "Основан", colors: "Цвета", coach: "Тренер", squad: "Состав", players: "игроков",
      yrs: "лет", notFound: "Команда не найдена",
      didYouKnow: {
        title: "А ты знал?",
        founded: "{team} основан в {year} году — это уже {age} лет футбольной истории!",
        venue: "Домашние матчи проходят на стадионе {venue} — это футбольный дом клуба.",
        competition: "В этом сезоне команда играет в турнире {competition}.",
        coach: "Главный тренер — {coach}; он помогает выбирать тактику и план тренировок.",
        squad: "В составе {count} игроков — можно собрать много разных вариантов команды.",
        colors: "Цвета клуба: {colors}; болельщики узнают их издалека.",
        fallbacks: [
          "Каждая эмблема рассказывает маленькую историю о {team}, городе или болельщиках.",
          "Футболисты обычно тренируются много раз в неделю перед матчем.",
          "Громкая поддержка дома может сделать матч ещё более захватывающим.",
        ],
      },
      pos: { goalkeeper: "Вратари", defence: "Защитники", midfield: "Полузащитники", offence: "Нападающие" },
    },
    player: {
      club: "Клуб", nationality: "Гражданство", age: "Возраст", born: "Родился",
      number: "Номер", contract: "Контракт", notFound: "Игрок не найден",
    },
    settings: { language: "Язык", title: "Настройки" },
    search: {
      placeholder: "Поиск команд и игроков...",
      teams: "Команды",
      players: "Игроки",
      noResults: "Ничего не найдено",
      hint: "Введите минимум 2 символа для поиска",
    },
    offline: "Нет сети - показываем сохранённые данные",
    loading: "Загрузка...",
    loadingSub: "Собираем последние результаты",
    nextMatch: {
      title: "Следующий матч твоей команды",
      home: "Дома",
      away: "В гостях",
      days: "Дн",
      hours: "Час",
      minutes: "Мин",
      seconds: "Сек",
    },
    matchStory: {
      title: "История матча",
      loading: "Ищем историю этого матча…",
      fallback: "Полный обзор этого матча пока не найден, но вот что понятно по результату.",
      fallbackBadge: "По счёту",
      sources: "Источники",
      source: "Источник",
      why: "Почему это важно",
      watchHighlights: "Смотреть хайлайты",
      error: "Не удалось загрузить историю прямо сейчас. Попробуйте открыть этот матч позже.",
    },
    story: {
      homeDominant: [
        "{home} уверенно разобрался с {away}.",
        "{home} оказался заметно сильнее {away}.",
      ],
      awayDominant: [
        "{away} уверенно победил {home} в гостях.",
        "{away} здорово сыграл на выезде против {home}.",
      ],
      homeControl: [
        "{home} спокойно обыграл {away}.",
        "{home} выглядел увереннее и победил {away}.",
      ],
      awayControl: [
        "{away} уверенно выиграл у {home} в гостях.",
        "{away} оказался собраннее и победил {home} на выезде.",
      ],
      homeControlClean: [
        "{home} обыграл {away} и не пропустил.",
        "{home} уверенно сыграл сзади и победил {away}.",
      ],
      awayControlClean: [
        "{away} победил {home} в гостях и сохранил ворота сухими.",
        "{away} надёжно сыграл в обороне и обыграл {home}.",
      ],
      homeNarrow: [
        "{home} чуть-чуть опередил {away}.",
        "{home} вырвал победу у {away} в близком матче.",
      ],
      awayNarrow: [
        "{away} оказался чуть сильнее {home} в гостях.",
        "{away} выжал победу над {home} в очень плотной игре.",
      ],
      homeNarrowClean: [
        "{home} взял минимальную победу над {away}.",
        "{home} удержал тонкое преимущество над {away}.",
      ],
      awayNarrowClean: [
        "{away} увёз минимальную победу от {home}.",
        "{away} сумел сохранить маленький перевес над {home}.",
      ],
      drawNoGoals: [
        "{home} и {away} не сумели открыть счёт.",
        "Матч {home} — {away} завершился без голов.",
      ],
      drawEven: [
        "{home} и {away} поделили очки.",
        "{home} и {away} сыграли вничью.",
      ],
      drawWild: [
        "{home} и {away} устроили яркую ничью {h}:{a}.",
        "В матче {home} — {away} голов было много, а победителя не оказалось.",
      ],
      summaryDominant: [
        "{winner} контролировал ход игры и победил со счётом {h}:{a}.",
        "{winner} чаще диктовал темп и уверенно довёл матч до победы {h}:{a}.",
      ],
      summaryDominantHighScoring: [
        "{winner} много атаковал и забил достаточно, чтобы оформить крупную победу {h}:{a}.",
        "У {winner} многое получалось впереди, поэтому счёт {h}:{a} выглядит вполне логично.",
      ],
      summaryDominantCleanSheet: [
        "{winner} сыграл надёжно в обороне и оставил свои ворота сухими — {h}:{a}.",
        "{winner} почти ничего не позволил сопернику и спокойно оформил победу {h}:{a}.",
      ],
      summaryControl: [
        "{winner} использовал свои моменты чуть лучше и взял победу {h}:{a}.",
        "Матч был под контролем у {winner}, и это принесло счёт {h}:{a}.",
      ],
      summaryControlCleanSheet: [
        "{winner} действовал собранно, не пропустил и выиграл {h}:{a}.",
        "Аккуратная игра сзади помогла {winner} довести матч до победы {h}:{a}.",
      ],
      summaryNarrow: [
        "Матч получился близким, но {winner} всё-таки выиграл {h}:{a}.",
        "До самого конца было напряжённо, однако {winner} удержал победу {h}:{a}.",
      ],
      summaryNarrowCleanSheet: [
        "{winner} сохранил минимальное преимущество и победил {h}:{a}.",
        "Одного точного удара хватило {winner}, чтобы завершить матч со счётом {h}:{a}.",
      ],
      summaryDrawNoGoals: [
        "Обе команды старались, но до гола дело так и не дошло.",
        "Моменты были нечастыми, поэтому встреча закончилась 0:0.",
      ],
      summaryDrawEven: [
        "У обеих команд были свои моменты, и встреча закончилась {h}:{a}.",
        "Игра вышла ровной, поэтому ничья {h}:{a} выглядит справедливой.",
      ],
      summaryDrawWild: [
        "Получилась весёлая игра с голами в обе стороны — {h}:{a}.",
        "Команды много атаковали, и матч завершился яркой ничьей {h}:{a}.",
      ],
    },
  },
  pt: {
    nav: { home: "Inicio", leagues: "Ligas", games: "Jogos", favorites: "Favoritos", login: "Entrar", logout: "Sair", search: "Procurar" },
    home: {
      title: "Goal Kick!",
      comingUp: "Proximos Jogos",
      todayMatches: "Jogos de Hoje",
      seeAll: "Ver tudo",
      noMatches: "Sem jogos agora",
      noMatchesSub: "Volta mais tarde ou explora as ligas!",
      stories: "Resumos dos Jogos",
      explore: "Explorar Ligas",
    },
    league: {
      table: "Classificacao",
      matches: "Jogos",
      topScorers: "Melhores Marcadores",
      upcoming: "Proximos",
      recentResults: "Resultados Recentes",
      noStandings: "Classificacao ainda nao disponivel",
      noMatches: "Sem jogos disponiveis",
      noScorers: "Marcadores nao disponiveis para esta competicao",
      pts: "pts",
      ast: "ass",
      played: "J", won: "V", drawn: "E", lost: "D", gd: "DG", points: "Pts", team: "Equipa",
    },
    login: {
      welcomeBack: "Bem-vindo de volta!",
      joinClub: "Junta-te ao Clube!",
      loginSub: "Entra para ver os teus favoritos",
      registerSub: "Cria a tua conta para guardar favoritos",
      name: "O teu nome",
      namePlaceholder: "ex. Alex",
      email: "Email",
      emailPlaceholder: "teu@email.com",
      password: "Palavra-passe",
      passwordPlaceholder: "A tua palavra-passe secreta",
      loginBtn: "Entrar",
      registerBtn: "Criar Conta",
      toggleLogin: "Ja tens conta? Entra",
      toggleRegister: "Novo aqui? Cria uma conta",
      skip: "Saltar - ver jogos",
    },
    favorites: {
      title: "Os Meus Favoritos",
      leagues: "Ligas",
      teams: "Equipas",
      empty: "Sem favoritos ainda",
      emptySub: "Explora as ligas e toca no coracao para guardar as tuas equipas favoritas!",
      browseBtn: "Explorar Ligas",
    },
    games: {
      title: "Jogos",
      subtitle: "Desafio diário de futebol",
      refresh: "Atualizar jogos",
      loadError: "Não foi possível carregar o jogo agora",
      submitError: "Não foi possível verificar a resposta",
      dailyQuiz: "Quiz diário",
      crestQuiz: "Quiz de emblemas",
      guessPlayer: "Adivinha o Jogador",
      guessCrest: "Adivinha o Emblema",
      submit: "Responder",
      checking: "A verificar...",
      doneToday: "Feito por hoje",
      correctToast: "Golo! Resposta certa",
      tryTomorrow: "Boa tentativa — novo quiz amanhã",
      alreadyPlayed: "Já jogaste o quiz de hoje. Volta amanhã para um novo!",
      scoreboard: "Marcador",
      points: "Pontos",
      streak: "Sequência",
      correct: "Certas",
      badges: "Emblemas",
      achievements: "Conquistas",
    },
    match: {
      live: "AO VIVO", ft: "FJ", ht: "Int.", today: "Hoje", tomorrow: "Amanha", matchday: "Jornada",
    },
    detail: {
      halfTime: "Int.", timeline: "Linha do Jogo", firstHalf: "1a Parte", secondHalf: "2a Parte",
      h2h: "Confronto Direto", meetings: "jogos", error: "Nao foi possivel carregar os detalhes do jogo",
      extraTime: "Apos prolongamento", penalties: "Apos penaltis",
      totalGoals: "golos em {n} jogos", winner: "Vencedor",
    },
    season: {
      matchday: "Jornada", of: "de", progress: "Progresso da Epoca",
    },
    team: {
      founded: "Fundado", colors: "Cores", coach: "Treinador", squad: "Plantel", players: "jogadores",
      yrs: "anos", notFound: "Equipa nao encontrada",
      didYouKnow: {
        title: "Sabias que?",
        founded: "{team} foi fundado em {year} — ja sao {age} anos de historia no futebol!",
        venue: "Os jogos em casa sao no {venue}, a casa futebolistica do clube.",
        competition: "Nesta epoca a equipa joga em {competition}.",
        coach: "O treinador e {coach}, quem prepara treinos e taticas.",
        squad: "O plantel tem {count} jogadores, por isso ha muitas escolhas para o onze.",
        colors: "As cores do clube sao {colors}; os adeptos reconhecem-nas de longe.",
        fallbacks: [
          "Cada emblema conta uma pequena historia sobre {team}, a cidade ou os adeptos.",
          "Os jogadores costumam treinar muitas vezes por semana antes do dia do jogo.",
          "Uma bancada cheia em casa pode tornar o jogo ainda mais emocionante.",
        ],
      },
      pos: { goalkeeper: "Guarda-redes", defence: "Defesas", midfield: "Medios", offence: "Avancados" },
    },
    player: {
      club: "Clube", nationality: "Nacionalidade", age: "Idade", born: "Nascimento",
      number: "Numero", contract: "Contrato", notFound: "Jogador nao encontrado",
    },
    settings: { language: "Idioma", title: "Definicoes" },
    search: {
      placeholder: "Procurar equipas e jogadores...",
      teams: "Equipas",
      players: "Jogadores",
      noResults: "Sem resultados",
      hint: "Escreve pelo menos 2 caracteres para pesquisar",
    },
    offline: "Estas offline - a mostrar dados guardados",
    loading: "A carregar...",
    loadingSub: "A obter os ultimos resultados",
    nextMatch: {
      title: "Proximo jogo da tua equipa",
      home: "Em casa",
      away: "Fora",
      days: "Dias",
      hours: "Horas",
      minutes: "Min",
      seconds: "Seg",
    },
    matchStory: {
      title: "História do Jogo",
      loading: "A procurar a história deste jogo…",
      fallback: "Ainda não encontrámos uma história completa deste jogo, mas aqui está o que sabemos pelo resultado.",
      fallbackBadge: "Pelo resultado",
      sources: "Fontes",
      source: "Fonte",
      why: "Porque importa",
      watchHighlights: "Ver highlights",
      error: "Não foi possível carregar a história agora. Tenta abrir este jogo mais tarde.",
    },
    story: {
      homeDominant: [
        "{home} foi claramente superior a {away}.",
        "{home} mandou no jogo contra {away}.",
      ],
      awayDominant: [
        "{away} foi mais forte fora de casa contra {home}.",
        "{away} controlou bem o jogo na casa do {home}.",
      ],
      homeControl: [
        "{home} venceu {away} com segurança.",
        "{home} foi mais consistente e bateu {away}.",
      ],
      awayControl: [
        "{away} venceu fora frente a {home} com segurança.",
        "{away} esteve mais estável e ganhou ao {home} fora de casa.",
      ],
      homeControlClean: [
        "{home} venceu {away} sem sofrer golos.",
        "{home} controlou o jogo e fechou a baliza contra {away}.",
      ],
      awayControlClean: [
        "{away} ganhou ao {home} fora de casa sem sofrer golos.",
        "{away} esteve muito seguro atrás e bateu {home}.",
      ],
      homeNarrow: [
        "{home} superou {away} por margem curta.",
        "{home} levou a melhor sobre {away} num jogo apertado.",
      ],
      awayNarrow: [
        "{away} ultrapassou {home} por margem mínima fora de casa.",
        "{away} foi mais feliz do que {home} num jogo muito equilibrado.",
      ],
      homeNarrowClean: [
        "{home} segurou uma vantagem mínima sobre {away}.",
        "{home} ganhou pela margem mínima frente a {away}.",
      ],
      awayNarrowClean: [
        "{away} segurou uma vitória curta na casa do {home}.",
        "{away} protegeu bem a vantagem mínima frente a {home}.",
      ],
      drawNoGoals: [
        "{home} e {away} ficaram no zero a zero.",
        "Nem {home} nem {away} conseguiram marcar.",
      ],
      drawEven: [
        "{home} e {away} dividiram os pontos.",
        "{home} e {away} terminaram empatados.",
      ],
      drawWild: [
        "{home} e {away} protagonizaram um empate animado de {h}-{a}.",
        "Houve golos para os dois lados no empate entre {home} e {away}.",
      ],
      summaryDominant: [
        "{winner} controlou bem o encontro e venceu por {h}-{a}.",
        "{winner} foi mais forte durante grande parte do jogo e ganhou por {h}-{a}.",
      ],
      summaryDominantHighScoring: [
        "{winner} atacou com força e construiu uma vitória larga por {h}-{a}.",
        "Com muita presença ofensiva, {winner} afastou-se no marcador até ao {h}-{a}.",
      ],
      summaryDominantCleanSheet: [
        "{winner} defendeu com segurança, não sofreu golos e ganhou por {h}-{a}.",
        "{winner} esteve firme atrás e confirmou uma vitória clara por {h}-{a}.",
      ],
      summaryControl: [
        "{winner} aproveitou melhor os momentos do jogo e venceu por {h}-{a}.",
        "{winner} foi mais eficaz e acabou por merecer o {h}-{a}.",
      ],
      summaryControlCleanSheet: [
        "{winner} manteve tudo organizado atrás e fechou o jogo em {h}-{a}.",
        "Sem sofrer golos, {winner} conduziu o jogo com calma até ao {h}-{a}.",
      ],
      summaryNarrow: [
        "Foi equilibrado até ao fim, mas {winner} conseguiu vencer por {h}-{a}.",
        "Houve pouco a separar as equipas, e {winner} acabou por ganhar {h}-{a}.",
      ],
      summaryNarrowCleanSheet: [
        "{winner} protegeu bem a vantagem mínima e ganhou por {h}-{a}.",
        "Um jogo apertado terminou com {winner} a segurar o {h}-{a}.",
      ],
      summaryDrawNoGoals: [
        "As duas equipas tentaram, mas o jogo terminou mesmo 0-0.",
        "Faltou o toque final, e o encontro acabou sem golos.",
      ],
      summaryDrawEven: [
        "As duas equipas tiveram bons momentos e o encontro acabou em {h}-{a}.",
        "Foi um jogo equilibrado, por isso o empate {h}-{a} faz sentido.",
      ],
      summaryDrawWild: [
        "Foi um empate divertido, com golos dos dois lados: {h}-{a}.",
        "O jogo foi aberto e animado, terminando em {h}-{a}.",
      ],
    },
  },
};

export function getTranslation(lang, key) {
  const keys = key.split(".");
  let value = translations[lang] || translations.en;
  for (const k of keys) {
    value = value?.[k];
    if (value === undefined) {
      // Fallback to English
      let fallback = translations.en;
      for (const fk of keys) fallback = fallback?.[fk];
      return fallback || key;
    }
  }
  return value;
}

export function localizeStory(story, lang) {
  const home = story.home_team?.name || "Home";
  const away = story.away_team?.name || "Away";
  const competition = story.competition?.name || "";
  const h = story.score?.home;
  const a = story.score?.away;
  if (h == null || a == null) return story;

  const winner = h > a ? home : away;
  const scoreLine = `${home} ${h}–${a} ${away}`;
  const competitionSuffix = competition ? ` · ${competition}` : "";
  const summaryByLang = {
    ru: h === a
      ? `Ничья: ${scoreLine}${competitionSuffix}.`
      : `Победитель: ${winner}. Счёт: ${scoreLine}${competitionSuffix}.`,
    pt: h === a
      ? `Empate: ${scoreLine}${competitionSuffix}.`
      : `Vencedor: ${winner}. Resultado: ${scoreLine}${competitionSuffix}.`,
    en: h === a
      ? `Draw: ${scoreLine}${competitionSuffix}.`
      : `Winner: ${winner}. Score: ${scoreLine}${competitionSuffix}.`,
  };

  return {
    ...story,
    headline: scoreLine,
    summary: summaryByLang[lang] || summaryByLang.en,
  };
}

export default translations;
