<?php
declare(strict_types=1);

namespace App\Repositories;

use RuntimeException;

/**
 * Signale une base injoignable, distincte d'une erreur de programmation.
 * public/index.php la traduit en 503, jamais en 500.
 */
final class DatabaseIndisponibleException extends RuntimeException
{
}
