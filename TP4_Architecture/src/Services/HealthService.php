<?php
declare(strict_types=1);

namespace App\Services;

use App\Repositories\Database;

/**
 * Vérifie que la base répond réellement (SELECT 1), pas seulement que PHP démarre.
 */
final class HealthService
{
    /**
     * @return array{statut: string, base: string, horodatage: string}
     */
    public function verifier(): array
    {
        $joignable = Database::estJoignable();

        return [
            'statut' => $joignable ? 'ok' : 'indisponible',
            'base' => $joignable ? 'ok' : 'erreur',
            'horodatage' => gmdate('c'),
        ];
    }
}
