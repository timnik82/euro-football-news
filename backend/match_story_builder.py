def build_child_match_story(match: dict, language: str, articles: list[dict]) -> dict:
    lang = language if language in {"en", "ru", "pt"} else "en"
    home = (match.get("homeTeam") or {}).get("shortName") or (match.get("homeTeam") or {}).get("name") or "Home"
    away = (match.get("awayTeam") or {}).get("shortName") or (match.get("awayTeam") or {}).get("name") or "Away"
    comp = (match.get("competition") or {}).get("name") or "football"
    score = match.get("score", {}).get("fullTime", {})
    half = match.get("score", {}).get("halfTime", {})
    h = score.get("home")
    a = score.get("away")
    match_date = (match.get("utcDate") or "")[:10]
    has_score = h is not None and a is not None
    winner = home if has_score and h > a else away if has_score and a > h else None
    is_draw = has_score and h == a
    source_names = [s.get("sourceName") for s in articles[:3] if s.get("sourceName")]
    source_phrase = ", ".join(source_names[:2])

    if lang == "ru":
        title = f"История матча: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} и {away} сыграли {h}:{a} в турнире {comp}. Обе команды получили по одному очку, а матч стал хорошим примером того, как важно сохранять концентрацию до финального свистка."
            else:
                summary = f"{winner} победил в матче {home} — {away} со счётом {h}:{a} в турнире {comp}. Это была важная игра, где решали точность, терпение и командная работа."
        else:
            summary = f"Матч {home} — {away} проходит в турнире {comp}. Мы собрали короткую и понятную историю по доступным данным матча."
        key_points = [
            f"Игра: {home} против {away}.",
            f"Турнир: {comp}.",
        ]
        if has_score:
            key_points.append(f"Итоговый счёт: {h}:{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"После первого тайма было {half.get('home')}:{half.get('away')}.")
        if articles:
            key_points.append(f"Мы нашли внешние источники по этому матчу: {source_phrase}.")
        why = "Этот результат важен, потому что каждая игра влияет на таблицу, уверенность команд и настроение болельщиков. По таким матчам удобно учиться читать счёт, замечать ход игры и понимать турнир."
        fallback_note = "Полный внешний обзор пока не найден, поэтому история составлена по данным матча."
    elif lang == "pt":
        title = f"História do jogo: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} e {away} empataram {h}-{a} em {comp}. As duas equipas somaram um ponto, num jogo que mostra como a concentração conta até ao fim."
            else:
                summary = f"{winner} venceu o jogo {home} — {away} por {h}-{a} em {comp}. Foi uma partida em que precisão, paciência e trabalho de equipa fizeram diferença."
        else:
            summary = f"O jogo {home} — {away} faz parte de {comp}. Reunimos uma história curta e simples com os dados disponíveis."
        key_points = [
            f"Jogo: {home} contra {away}.",
            f"Competição: {comp}.",
        ]
        if has_score:
            key_points.append(f"Resultado final: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"Ao intervalo estava {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"Encontrámos fontes externas sobre este jogo: {source_phrase}.")
        why = "Este resultado importa porque cada jogo mexe com a tabela, a confiança das equipas e a energia dos adeptos. Também ajuda a aprender a ler resultados e a perceber uma competição."
        fallback_note = "Ainda não encontrámos uma reportagem completa, por isso a história usa os dados do jogo."
    else:
        title = f"Story of the Match: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} and {away} finished {h}-{a} in {comp}. Both teams earned one point, and the match showed why focus matters until the final whistle."
            else:
                summary = f"{winner} won the match between {home} and {away} by {h}-{a} in {comp}. It was a game where accuracy, patience, and teamwork made the difference."
        else:
            summary = f"{home} and {away} meet in {comp}. Here is a short, simple story from the match information we have so far."
        key_points = [
            f"Match: {home} against {away}.",
            f"Competition: {comp}.",
        ]
        if has_score:
            key_points.append(f"Final score: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"At half-time it was {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"External match sources were found, including {source_phrase}.")
        why = "This result matters because every match can shape the table, team confidence, and supporter excitement. It is also a great way to learn how scores and competitions work."
        fallback_note = "We could not find a full story for this match yet, so this story uses the match result data."

    if not articles and fallback_note not in key_points:
        key_points.append(fallback_note)

    image_url = next((a.get("imageUrl") for a in articles if a.get("imageUrl")), None)
    video_url = next((a.get("videoUrl") for a in articles if a.get("videoUrl")), None)
    return {
        "title": title,
        "summary": summary,
        "keyPoints": key_points[:5],
        "whyItMatters": why,
        "isFallback": len(articles) == 0,
        "imageUrl": image_url,
        "sources": articles[:3],
        "videoUrl": video_url,
        "matchDate": match_date,
    }
