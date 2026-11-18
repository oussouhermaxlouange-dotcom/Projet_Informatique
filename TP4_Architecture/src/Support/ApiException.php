<?php
declare(strict_types=1);

namespace App\Support;

use RuntimeException;

/**
 * Exception métier portant le code HTTP et le code d'erreur de l'API.
 * Le contrôleur ne construit pas la réponse d'erreur lui-même :
 * public/index.php la convertit en JSON, ce qui garde les contrôleurs courts.
 */
final class ApiException extends RuntimeException
{
    /**
     * @param array<string, mixed> $details
     */
    public function __construct(
        public readonly int $statut,
        public readonly string $codeErreur,
        string $message,
        public readonly array $details = []
    ) {
        parent::__construct($message);
    }
}
