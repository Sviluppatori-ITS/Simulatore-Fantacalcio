import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { fetchPlayers } from '../services/playerApi';
import type { Player } from '../services/playerApi';

export default function Players() {
    const [players, setPlayers] = useState<Player[]>([]);
    const [error, setError] = useState<string | null>(null);

    const ROLE_LABELS: Record<string, string> = {
        P: 'Portiere',
        D: 'Difensore',
        C: 'Centrocampista',
        A: 'Attaccante',
    };

    // Prendo la query string dalla URL
    const { search } = useLocation();

    // Converto la query string in un oggetto filtro
    function parseFilters(search: string) {
        const params = new URLSearchParams(search);
        const filters: Record<string, string> = {};
        params.forEach((value, key) => {
            filters[key] = value;
        });
        return filters;
    }

    useEffect(() => {
        const filters = parseFilters(search);
        fetchPlayers(filters)
            .then(setPlayers)
            .catch(e => setError(e.message));
    }, [search]);

    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>Players</h2>
            <ol type="I">
                {players.map(p => (
                    <li key={p.id}>
                        Nome: {p.person.name} <br />
                        Cognome: {p.person.surname} <br />
                        Data di nascita:{' '}
                        {p.person.birth_date
                            ? new Date(p.person.birth_date).toLocaleDateString('it-IT', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                              })
                            : 'N/A'}{' '}
                        <br />
                        Ruolo: {ROLE_LABELS[p.main_role || ''] || p.main_role} <br />
                        Overall: {p.overall} <br />
                        Fanta Value: {p.fanta_value} <br />
                        Valore mercato: {p.value} <br />
                        Nazionalità: {p.person.main_nationality_info?.name ?? 'N/A'} <br />
                        Altre nazionalità:{' '}
                        {p.person.other_nationalities_info?.length
                            ? p.person.other_nationalities_info.map(n => n.name).join(', ')
                            : 'Nessuna'}{' '}
                        <br />
                        <hr />
                    </li>
                ))}
            </ol>
        </div>
    );
}
