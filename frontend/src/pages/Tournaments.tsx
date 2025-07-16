import { useEffect, useState } from 'react';

interface Tournament {
    id: number;
    name: string;
    description?: string;
}

export default function Tournaments() {
    const [tournaments, setTournaments] = useState<Tournament[]>([]);

    useEffect(() => {
        fetch('/api/tournaments/')
            .then(res => res.json())
            .then(data => setTournaments(data))
            .catch(console.error);
    }, []);

    return (
        <div>
            <h2>Tournaments</h2>
            <ul>
                {tournaments.map(t => (
                    <li key={t.id}>
                        {t.name} - {t.description}
                    </li>
                ))}
            </ul>
        </div>
    );
}
