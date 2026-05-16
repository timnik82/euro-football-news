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
    source_names = []
    for article in articles[:3]:
        source_name = article.get("sourceName")
        if source_name and source_name not in source_names:
            source_names.append(source_name)
    source_phrase = ", ".join(source_names[:2])

    if lang == "ru":
        title = f"История матча: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} — {away}: {h}:{a}. Турнир: {comp}."
            else:
                summary = f"Победитель: {winner}. Счёт: {home} — {away} {h}:{a}. Турнир: {comp}."
        else:
            summary = f"Матч {home} — {away}. Турнир: {comp}."
        key_points = [
            f"Игра: {home} против {away}.",
            f"Турнир: {comp}.",
        ]
        if has_score:
            key_points.append(f"Итоговый счёт: {h}:{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"После первого тайма было {half.get('home')}:{half.get('away')}.")
        if articles:
            key_points.append(f"Источники: {source_phrase}.")
        why = f"Факты матча: {home} — {away}, {comp}."
    elif lang == "pt":
        title = f"História do jogo: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} — {away}: {h}-{a}. Competição: {comp}."
            else:
                summary = f"{winner} venceu: {home} — {away} {h}-{a}. Competição: {comp}."
        else:
            summary = f"Jogo {home} — {away}. Competição: {comp}."
        key_points = [
            f"Jogo: {home} contra {away}.",
            f"Competição: {comp}.",
        ]
        if has_score:
            key_points.append(f"Resultado final: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"Ao intervalo estava {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"Fontes: {source_phrase}.")
        why = f"Factos do jogo: {home} — {away}, {comp}."
    else:
        title = f"Story of the Match: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} — {away}: {h}-{a}. Competition: {comp}."
            else:
                summary = f"{winner} won: {home} — {away} {h}-{a}. Competition: {comp}."
        else:
            summary = f"Match: {home} — {away}. Competition: {comp}."
        key_points = [
            f"Match: {home} against {away}.",
            f"Competition: {comp}.",
        ]
        if has_score:
            key_points.append(f"Final score: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"At half-time it was {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"Sources: {source_phrase}.")
        why = f"Match facts: {home} — {away}, {comp}."

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
