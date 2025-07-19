# 🌍 Geografia e Identità
from .continent import Continent
from .nationality import Nationality
from .person import Person

# 👥 Persone
from .player import Player
from .staff import Staff
from .manager import Manager

# 🏟️ Squadre e Organizzazione
from .team import Team
from .roster_slot import RosterSlot
from .season_team import SeasonTeam

# 📊 Statistiche e Storico
from .player_statistics import PlayerStatistics
from .match_history import MatchHistory
from .ranking import Ranking

# 🏆 Tornei e Regole
from .tournament import Tournament
from .tournament_structure import TournamentStructure
from .tournament_rule import TournamentRule
from .tournament_qualification_rule import TournamentQualificationRule
from .tournament_ranking import TournamentRanking
from .trophy import Trophy

# 🗓️ Stagioni, Leghe, Giornate
from .season import Season
from .league import League
from .round import Round

# 🕹️ Partite e Eventi
from .match import Match
from .match_event import MatchEvent

# 📐 Formazioni
from .formation import Formation
from .default_formation import DefaultFormation

# 🔁 Trasferimenti
from .transfer import Transfer

__all__ = [
    # Geografia e Identità
    'Continent',
    'Nationality',
    'Person',

    # Persone
    'Player',
    'Staff',
    'Manager',

    # Squadre e Organizzazione
    'Team',
    'RosterSlot',
    'SeasonTeam',

    # Statistiche e Storico
    'PlayerStatistics',
    'MatchHistory',
    'Ranking',

    # Tornei e Regole
    'Tournament',
    'TournamentStructure',
    'TournamentRule',
    'TournamentQualificationRule',
    'TournamentRanking',
    'Trophy',

    # Stagioni, Leghe, Giornate
    'Season',
    'League',
    'Round',

    # Partite e Eventi
    'Match',
    'MatchEvent',

    # Formazioni
    'Formation',
    'DefaultFormation',

    # Trasferimenti
    'Transfer',
]
