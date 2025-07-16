import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/setupTests.ts',
        reporters: ['default', ['junit', { outputFile: 'frontend/test-results/results.xml' }]],
    },
});
