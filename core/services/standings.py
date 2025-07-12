from core.models import Match, TournamentRule


def get_tournament_standings(tournament):
    rules = tournament.rules.filter(is_active=True).order_by('priority')
    matches = tournament.matches.filter(played=True)

    standings = {}
    for team in tournament.teams.all():
        standings[team] = {
            'points': 0,
            'goals_for': 0,
            'goals_against': 0,
            # altri criteri opzionali
        }

    for match in matches:
        h, a = match.home_team, match.away_team
        hs, as_ = match.home_score, match.away_score

        standings[h]['goals_for'] += hs
        standings[h]['goals_against'] += as_
        standings[a]['goals_for'] += as_
        standings[a]['goals_against'] += hs

        rule_win = rules.get(rule_type='point_win').value
        rule_draw = rules.get(rule_type='point_draw').value
        rule_loss = rules.get(rule_type='point_loss').value

        if hs > as_:
            standings[h]['points'] += rule_win
            standings[a]['points'] += rule_loss
        elif hs < as_:
            standings[a]['points'] += rule_win
            standings[h]['points'] += rule_loss
        else:
            standings[h]['points'] += rule_draw
            standings[a]['points'] += rule_draw

    sorted_teams = sorted(
        standings.items(),
        key=lambda x: (
            x[1]['points'],
            x[1]['goals_for'] - x[1]['goals_against']
        ),
        reverse=True
    )

    return sorted_teams
