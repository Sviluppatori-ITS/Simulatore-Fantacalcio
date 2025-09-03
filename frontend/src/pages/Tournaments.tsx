import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { fetchTournaments } from '../services/tournamentsApi';
import type { Tournament } from '../services/tournamentsApi';

export default function Tournaments() {
    const [tournaments, setTournaments] = useState<Tournament[]>([]);
    const [error, setError] = useState<string | null>(null);

    const { search } = useLocation();

    function parseFilters(search: string) {
        const params = new URLSearchParams(search);
        const filters: Record<string, string> = {};
        params.forEach((value, key) => {
            filters[key] = value;
        });
        return filters;
    }

    function formatDate(date: string | null | undefined) {
        if (!date) return 'N/A';
        return new Date(date).toLocaleDateString('it-IT', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
        });
    }

    useEffect(() => {
        const filters = parseFilters(search);
        fetchTournaments(filters)
            .then(setTournaments)
            .catch(e => setError(e.message));
    }, [search]);

    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>Tournaments</h2>
            <ol type="I">
                {tournaments.map(t => (
                    <li key={t.id}>
                        <strong>{t.name}</strong> <br />
                        Descrizione: {t.description ?? 'N/A'} <br />
                        Inizio: {formatDate(t.start_date)} <br />
                        Fine: {formatDate(t.end_date)} <br />
                        Attivo: {t.is_active ? 'Sì' : 'No'} <br />
                        Giornata attuale: {t.current_match_day} <br />
                        Logo:{' '}
                        {t.logo ? (
                            <img src={t.logo} alt="logo" style={{ height: '40px' }} />
                        ) : (
                            'Nessuno'
                        )}{' '}
                        <br />
                        <details>
                            <summary>
                                <strong>Struttura</strong>
                            </summary>
                            <ul>
                                <li>Coppa: {t.structure.is_cup ? 'Sì' : 'No'}</li>
                                <li>Gironi: {t.structure.use_groups ? 'Sì' : 'No'}</li>
                                <li>Andata/Ritorno: {t.structure.home_and_away ? 'Sì' : 'No'}</li>
                                {/* I nuovi campi saranno visibili dopo l'aggiornamento dell'API */}
                                {/* <li>Pareggi consentiti: {t.structure.allow_draws ? 'Sì' : 'No'}</li> */}
                                {/* {!t.structure.allow_draws && (
                                    <li>
                                        Metodo di risoluzione pareggi: {
                                            {
                                                'penalties': 'Calci di rigore',
                                                'extra_time': 'Tempi supplementari',
                                                'extra_time_penalties': 'Tempi supplementari e rigori',
                                                'replay': 'Ripetizione della partita',
                                                'golden_goal': 'Golden goal'
                                            }[t.structure.draw_resolution] || t.structure.draw_resolution
                                        }
                                    </li>
                                )} */}
                                {/* Questi campi saranno visibili dopo l'aggiornamento dell'API */}
                                {/* <li>
                                    Punti: {t.structure.POINTS_WIN} vittoria, {t.structure.POINTS_DRAW} pareggio, {t.structure.POINTS_LOSS} sconfitta
                                </li>
                                {!t.structure.allow_draws && (
                                    <li>
                                        Punti speciali: {t.structure.POINTS_WIN_SHOOTOUT} vittoria ai rigori, {t.structure.POINTS_LOSS_SHOOTOUT} sconfitta ai rigori, {t.structure.POINTS_WIN_EXTRA_TIME} vittoria ai supplementari
                                    </li>
                                )} */}
                                <li>
                                    Playoff:{' '}
                                    {t.structure.has_playoff
                                        ? `Sì (${t.structure.playoff_teams} squadre)`
                                        : 'No'}
                                </li>
                                <li>
                                    Playout:{' '}
                                    {t.structure.has_playout
                                        ? `Sì (${t.structure.playout_teams} squadre)`
                                        : 'No'}
                                </li>
                                <li>
                                    Retrocessione abilitata:{' '}
                                    {t.structure.relegation_enabled
                                        ? `Sì (${t.structure.relegation_teams} squadre)`
                                        : 'No'}
                                </li>
                                <li>Posti qualificazione: {t.structure.qualification_spots}</li>
                            </ul>
                        </details>
                        <details>
                            <summary>
                                <strong>Stagione</strong>
                            </summary>
                            Anno: {t.season.year} <br />
                            Attiva: {t.season.is_active ? 'Sì' : 'No'}
                        </details>
                        <details>
                            <summary>
                                <strong>Trofeo</strong>
                            </summary>
                            Nome: {t.trophy?.name ?? 'Nessuno'} <br />
                            Descrizione: {t.trophy?.description ?? 'N/A'} <br />
                            {t.trophy?.trophy_img ? (
                                <img
                                    src={t.trophy.trophy_img}
                                    alt="trophy"
                                    style={{ height: '40px' }}
                                />
                            ) : (
                                'Nessuna immagine'
                            )}
                        </details>
                        <details>
                            <summary>
                                <strong>Squadre partecipanti</strong>
                            </summary>
                            {t.teams?.length ? (
                                <ul>
                                    {t.teams.map(season_team => (
                                        <li key={season_team.id}>
                                            ID: {season_team.id} <br />
                                            <details>
                                                <summary>
                                                    <strong>Team</strong>
                                                </summary>
                                                <ul>
                                                    <li>
                                                        {season_team.team.name} (
                                                        {season_team.team.code})
                                                        <details>
                                                            <summary>
                                                                <strong>Owner</strong>
                                                            </summary>
                                                            {season_team.team.owner ? (
                                                                <ul>
                                                                    <li>
                                                                        ID:{' '}
                                                                        {season_team.team.owner.id}
                                                                    </li>
                                                                    <li>
                                                                        Username:{' '}
                                                                        {
                                                                            season_team.team.owner
                                                                                .username
                                                                        }
                                                                    </li>
                                                                    <li>
                                                                        Email:{' '}
                                                                        {
                                                                            season_team.team.owner
                                                                                .email
                                                                        }
                                                                    </li>
                                                                </ul>
                                                            ) : (
                                                                <p>Nessun owner</p>
                                                            )}
                                                        </details>
                                                    </li>
                                                </ul>
                                            </details>
                                            <details>
                                                <summary>
                                                    <strong>Stagione</strong>
                                                </summary>
                                                Anno: {season_team.season.year} <br />
                                                Attiva: {season_team.season.is_active ? 'Sì' : 'No'}
                                            </details>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                'Nessuna squadra'
                            )}
                        </details>
                        Creato il: {formatDate(t.created_at)} <br />
                        Ultima modifica: {formatDate(t.updated_at)} <br />
                        <hr />
                    </li>
                ))}
            </ol>
        </div>
    );
}
