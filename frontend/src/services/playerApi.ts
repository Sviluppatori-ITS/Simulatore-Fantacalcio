export interface Player {
    id: number;
    person: {
        id: number;
        name: string;
        surname: string;
        birth_date?: string;
        main_nationality_info?: {
            id: number;
            name: string;
            code: string;
            continent: {
                id: number;
                name: string;
                code: string;
            };
        };
        other_nationalities_info?: {
            id: number;
            name: string;
            code: string;
            continent: {
                id: number;
                name: string;
                code: string;
            };
        }[];
    };
    main_role: string | null;
    overall: number;
    fanta_value: number;
    value: number;
}

export async function fetchPlayers(): Promise<Player[]> {
    const res = await fetch('/api/player/');
    if (!res.ok) throw new Error('Failed to fetch players');
    return res.json();
}
