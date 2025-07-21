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
            <ol>
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
                                    {t.teams.map(team => (
                                        <li key={team.id}>
                                            {team.name} ({team.code}){' '}
                                            {team.owner ? `– Proprietario: ${team.owner}` : ''}
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
