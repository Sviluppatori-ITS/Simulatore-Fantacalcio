// src/api/tournaments.ts
import { apiFetch } from './api';

export interface Tournament {
    id: number;
    name: string;
    description?: string;
    start_date: string;
    end_date: string;
    is_active: boolean;
    current_match_day: number;
    logo: string | null;
    structure: {
        id: number;
        is_cup: boolean;
        use_groups: boolean;
        home_and_away: boolean;
        has_playoff: boolean;
        has_playout: boolean;
        relegation_enabled: boolean;
        relegation_teams: number;
        playoff_teams: number;
        playout_teams: number;
        qualification_spots: number;
        created_at: string;
        updated_at: string;
    };
    season: {
        id: number;
        year: number;
        is_active: boolean;
        created_at: string;
        updated_at: string;
        league: number;
    };
    teams?: {
        id: number;
        name: string;
        code: string;
        owner?: {
            id: number;
        };
        created_at: string;
        updated_at: string;
    }[];
    trophy: {
        id: number;
        name: string;
        description: string;
        trophy_img: string | null;
        created_at: string;
        updated_at: string;
        awarded_to: number | null;
    };
    created_at: string;
    updated_at: string;
}

export interface TournamentFilters {
    [key: string]: string | number | undefined;
}

export async function fetchTournaments(filters?: TournamentFilters): Promise<Tournament[]> {
    let url = '/api/tournament/';
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
    if (!res.ok) throw new Error('Failed to fetch tournaments');
    return res.json();
}
