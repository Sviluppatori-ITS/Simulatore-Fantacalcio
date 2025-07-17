import { apiFetch } from './api';

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

export interface PlayerFilters {
    [key: string]: string | number | undefined;
}

export async function fetchPlayers(filters?: PlayerFilters) {
    let url = '/api/player/';
    if (filters) {
        const params = new URLSearchParams();
        for (const key in filters) {
            const val = filters[key];
            if (val !== undefined && val !== null && val !== '') {
                params.append(key, String(val));
            }
        }
        url += `?${params.toString()}`;
    }

    const res = await apiFetch(url);
    if (!res.ok) throw new Error('Failed to fetch players');
    return res.json();
}
