import { CalendarDays, ClipboardList, MapPin, Palette, Sparkles, Trophy, UsersRound } from "lucide-react";

const currentYear = new Date().getFullYear();

const fill = (template, values) => Object.entries(values).reduce(
  (text, [key, value]) => text.replaceAll(`{${key}}`, value ?? ""),
  template,
);

const factIconClass = "w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0";

function buildFacts(team, t) {
  const teamName = team.shortName || team.name;
  const facts = [];

  if (team.founded) {
    facts.push({
      icon: CalendarDays,
      iconClass: "bg-sky-100 text-sky-600",
      text: fill(t("team.didYouKnow.founded"), {
        team: teamName,
        year: team.founded,
        age: Math.max(currentYear - Number(team.founded), 1),
      }),
    });
  }

  if (team.venue) {
    facts.push({
      icon: MapPin,
      iconClass: "bg-green-100 text-green-700",
      text: fill(t("team.didYouKnow.venue"), { venue: team.venue }),
    });
  }

  const mainCompetition = team.runningCompetitions?.[0]?.name;
  if (mainCompetition) {
    facts.push({
      icon: Trophy,
      iconClass: "bg-yellow-100 text-yellow-700",
      text: fill(t("team.didYouKnow.competition"), { competition: mainCompetition }),
    });
  }

  if (team.coach?.name) {
    facts.push({
      icon: ClipboardList,
      iconClass: "bg-orange-100 text-orange-600",
      text: fill(t("team.didYouKnow.coach"), { coach: team.coach.name }),
    });
  }

  if (team.squadCount) {
    facts.push({
      icon: UsersRound,
      iconClass: "bg-blue-100 text-blue-700",
      text: fill(t("team.didYouKnow.squad"), { count: team.squadCount }),
    });
  }

  if (team.clubColors) {
    facts.push({
      icon: Palette,
      iconClass: "bg-red-100 text-red-600",
      text: fill(t("team.didYouKnow.colors"), { colors: team.clubColors }),
    });
  }

  return [...facts, ...t("team.didYouKnow.fallbacks").map((text) => ({
    icon: Sparkles,
    iconClass: "bg-slate-100 text-slate-600",
    text: fill(text, { team: teamName }),
  }))].slice(0, 3);
}

export const TeamFunFacts = ({ team, t }) => {
  const facts = buildFacts(team, t);

  return (
    <section
      className="card-tactile overflow-hidden mb-6 animate-slide-up"
      style={{ animationDelay: "0.13s" }}
      data-testid="team-did-you-know-section"
    >
      <div className="bg-gradient-to-r from-orange-50 via-white to-sky-50 px-5 py-4 border-b-2 border-slate-100">
        <div className="flex items-center gap-2">
          <Sparkles size={22} strokeWidth={2.5} className="text-orange-500" />
          <h2 className="text-xl sm:text-2xl font-black text-slate-800" data-testid="team-did-you-know-title">
            {t("team.didYouKnow.title")}
          </h2>
        </div>
      </div>
      <div className="grid gap-0 sm:grid-cols-3">
        {facts.map(({ icon: Icon, iconClass, text }, index) => (
          <div
            key={`${text}-${index}`}
            className={`flex gap-3 p-4 ${index < facts.length - 1 ? "border-b sm:border-b-0 sm:border-r" : ""} border-slate-100`}
            data-testid={`team-did-you-know-fact-${index + 1}`}
          >
            <div className={`${factIconClass} ${iconClass}`} data-testid={`team-did-you-know-fact-${index + 1}-icon`}>
              <Icon size={19} strokeWidth={2.5} />
            </div>
            <p className="text-sm font-bold leading-snug text-slate-700" data-testid={`team-did-you-know-fact-${index + 1}-text`}>
              {text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};