import { render, screen } from '@testing-library/react';
import Players from '../pages/Players';

describe('Players component', () => {
    it('renders heading', () => {
        render(<Players />);
        expect(screen.getByRole('heading', { name: /players/i })).toBeInTheDocument();
    });
});
