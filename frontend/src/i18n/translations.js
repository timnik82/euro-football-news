export const LANGUAGES = [
  { code: "en", label: "English", short: "EN" },
  { code: "ru", label: "Русский", short: "RU" },
  { code: "pt", label: "Português", short: "PT" },
];

export const DATE_LOCALES = { en: "en-GB", ru: "ru-RU", pt: "pt-PT" };

const translations = {
  en: {
    nav: { home: "Home", leagues: "Leagues", favorites: "Favorites", login: "Login", logout: "Logout" },
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
    nav: { home: "Главная", leagues: "Лиги", favorites: "Избранное", login: "Войти", logout: "Выход" },
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
    nav: { home: "Inicio", leagues: "Ligas", favorites: "Favoritos", login: "Entrar", logout: "Sair" },
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
  const t = (key) => getTranslation(lang, `story.${key}`);
  const home = story.home_team?.name || "Home";
  const away = story.away_team?.name || "Away";
  const h = story.score?.home;
  const a = story.score?.away;
  if (h == null || a == null) return story;

  const total = h + a;
  const diff = Math.abs(h - a);
  const winner = h > a ? home : away;
  const loser = h > a ? away : home;
  const cleanSheet = h === 0 || a === 0;
  const seedSource = `${story.match_id || ""}-${home}-${away}`;
  const seed = [...seedSource].reduce((acc, char) => acc + char.charCodeAt(0), 0);

  const pick = (key, offset = 0) => {
    const value = t(key);
    if (Array.isArray(value)) {
      return value[(seed + offset) % value.length];
    }
    return value;
  };

  let headlineKey;
  let summaryKey;

  if (h === a) {
    if (total === 0) {
      headlineKey = "drawNoGoals";
      summaryKey = "summaryDrawNoGoals";
    } else if (total >= 4) {
      headlineKey = "drawWild";
      summaryKey = "summaryDrawWild";
    } else {
      headlineKey = "drawEven";
      summaryKey = "summaryDrawEven";
    }
  } else {
    const prefix = h > a ? "home" : "away";

    if (diff >= 3) {
      headlineKey = `${prefix}Dominant`;
      summaryKey = cleanSheet
        ? "summaryDominantCleanSheet"
        : total >= 5
          ? "summaryDominantHighScoring"
          : "summaryDominant";
    } else if (diff === 2) {
      headlineKey = cleanSheet ? `${prefix}ControlClean` : `${prefix}Control`;
      summaryKey = cleanSheet ? "summaryControlCleanSheet" : "summaryControl";
    } else {
      headlineKey = cleanSheet ? `${prefix}NarrowClean` : `${prefix}Narrow`;
      summaryKey = cleanSheet ? "summaryNarrowCleanSheet" : "summaryNarrow";
    }
  }

  const fill = (template) => template
    .replaceAll("{home}", home)
    .replaceAll("{away}", away)
    .replaceAll("{winner}", winner)
    .replaceAll("{loser}", loser)
    .replaceAll("{h}", h)
    .replaceAll("{a}", a);

  return {
    ...story,
    headline: fill(pick(headlineKey)),
    summary: fill(pick(summaryKey, 1)),
  };
}

export default translations;
