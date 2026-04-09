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
    },
    settings: { language: "Language", title: "Settings" },
    offline: "You're offline - showing cached data",
    loading: "Loading...",
    loadingSub: "Getting the latest scores",
    story: {
      crushHome: "{home} crushes {away} in dominant display!",
      edgeHome: "{home} edges past {away} in tight game!",
      winHome: "{home} wins comfortably against {away}!",
      crushAway: "{away} demolishes {home} away from home!",
      edgeAway: "{away} sneaks a win at {home}!",
      winAway: "{away} triumphs at {home}!",
      draw0: "{home} and {away} play out goalless draw",
      drawGoals: "Exciting {h}-{a} draw between {home} and {away}!",
      goalfest: "A thrilling goal-fest that had fans on the edge of their seats!",
      entertaining: "An entertaining match with plenty of action!",
      defensive: "A defensive masterclass from both sides.",
      competitive: "A competitive battle on the pitch!",
      finalScore: "The final score was {h}-{a}.",
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
    },
    settings: { language: "Язык", title: "Настройки" },
    offline: "Нет сети - показываем сохранённые данные",
    loading: "Загрузка...",
    loadingSub: "Собираем последние результаты",
    story: {
      crushHome: "{home} разгромил {away}!",
      edgeHome: "{home} с трудом обыграл {away}!",
      winHome: "{home} уверенно обыграл {away}!",
      crushAway: "{away} разнёс {home} на выезде!",
      edgeAway: "{away} вырвал победу у {home}!",
      winAway: "{away} побеждает на выезде у {home}!",
      draw0: "{home} и {away} сыграли вничью 0:0",
      drawGoals: "Яркая ничья {h}:{a} между {home} и {away}!",
      goalfest: "Настоящий голевой фейерверк!",
      entertaining: "Зрелищный матч с множеством моментов!",
      defensive: "Оборонительный шедевр от обеих команд.",
      competitive: "Упорная борьба на поле!",
      finalScore: "Итоговый счёт {h}:{a}.",
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
    },
    settings: { language: "Idioma", title: "Definicoes" },
    offline: "Estas offline - a mostrar dados guardados",
    loading: "A carregar...",
    loadingSub: "A obter os ultimos resultados",
    story: {
      crushHome: "{home} esmaga {away} em exibicao dominante!",
      edgeHome: "{home} vence {away} por pouco!",
      winHome: "{home} vence {away} com tranquilidade!",
      crushAway: "{away} arrasa {home} fora de casa!",
      edgeAway: "{away} rouba a vitoria ao {home}!",
      winAway: "{away} triunfa em casa do {home}!",
      draw0: "{home} e {away} empatam sem golos",
      drawGoals: "Empate emocionante {h}-{a} entre {home} e {away}!",
      goalfest: "Uma verdadeira chuva de golos!",
      entertaining: "Um jogo divertido com muita acao!",
      defensive: "Uma aula de defesa de ambas as equipas.",
      competitive: "Uma batalha competitiva em campo!",
      finalScore: "O resultado final foi {h}-{a}.",
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
  let headlineKey;

  if (h > a) {
    headlineKey = diff >= 3 ? "crushHome" : diff === 1 ? "edgeHome" : "winHome";
  } else if (a > h) {
    headlineKey = diff >= 3 ? "crushAway" : diff === 1 ? "edgeAway" : "winAway";
  } else {
    headlineKey = total === 0 ? "draw0" : "drawGoals";
  }

  const flavorKey = total >= 5 ? "goalfest" : total >= 3 ? "entertaining" : total === 0 ? "defensive" : "competitive";

  const fill = (s) => s.replace("{home}", home).replace("{away}", away).replace("{h}", h).replace("{a}", a);

  return {
    ...story,
    headline: fill(t(headlineKey)),
    summary: `${fill(t("finalScore"))} ${t(flavorKey)}`,
  };
}

export default translations;
