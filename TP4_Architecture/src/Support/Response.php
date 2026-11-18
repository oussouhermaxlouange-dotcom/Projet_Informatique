<?php
declare(strict_types=1);

namespace App\Support;

/**
 * Réponse HTTP JSON. Le contrôleur retourne un objet Response ;
 * seul public/index.php l'envoie au client, ce qui rend les tests unitaires possibles.
 */
final class Response
{
    /**
     * @param array<string, mixed> $corps
     */
    public function __construct(public readonly int $code, public readonly array $corps)
    {
    }

    /**
     * @param array<string, mixed> $details
     */
    public static function erreur(int $code, string $codeErreur, string $message, array $details = []): self
    {
        $erreur = [
            'code' => $codeErreur,
            'message' => $message,
        ];

        if ($details !== []) {
            $erreur['details'] = $details;
        }

        return new self($code, ['erreur' => $erreur]);
    }

    public function envoyer(): void
    {
        http_response_code($this->code);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        header('X-Content-Type-Options: nosniff');

        echo json_encode(
            $this->corps,
            JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR
        ), "\n";
    }
}
