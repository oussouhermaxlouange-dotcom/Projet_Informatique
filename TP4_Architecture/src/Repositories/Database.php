<?php
declare(strict_types=1);

namespace App\Repositories;

use PDO;
use PDOException;
use Throwable;

/**
 * Point unique de création de la connexion PDO.
 * Le SQL métier reste dans les dépôts ; cette classe ne fournit que la connexion.
 */
final class Database
{
    private static ?PDO $pdo = null;

    public static function connexion(): PDO
    {
        if (self::$pdo instanceof PDO) {
            return self::$pdo;
        }

        $racine = dirname(__DIR__, 2);

        /** @var array{host: string, port: string, base: string, utilisateur: string, mot_de_passe: string, socket: ?string, charset: string} $config */
        $config = require $racine . '/config/database.php';

        $dsn = self::construireDsn($config);

        try {
            self::$pdo = new PDO($dsn, $config['utilisateur'], $config['mot_de_passe'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
                PDO::ATTR_TIMEOUT => 3,
            ]);
        } catch (PDOException $exception) {
            // Le message d'origine peut contenir l'hôte et l'utilisateur : on journalise,
            // mais on ne le renvoie jamais tel quel au navigateur.
            error_log('Connexion PDO impossible : ' . $exception->getMessage());

            throw new DatabaseIndisponibleException('Base de données indisponible.', 0, $exception);
        }

        return self::$pdo;
    }

    public static function estJoignable(): bool
    {
        try {
            self::connexion()->query('SELECT 1');

            return true;
        } catch (Throwable) {
            return false;
        }
    }

    /**
     * Utilisé par les tests pour repartir d'une connexion neuve.
     */
    public static function reinitialiser(): void
    {
        self::$pdo = null;
    }

    /**
     * @param array{host: string, port: string, base: string, socket: ?string, charset: string} $config
     */
    private static function construireDsn(array $config): string
    {
        if ($config['socket'] !== null && $config['socket'] !== '') {
            return sprintf(
                'mysql:unix_socket=%s;dbname=%s;charset=%s',
                $config['socket'],
                $config['base'],
                $config['charset']
            );
        }

        return sprintf(
            'mysql:host=%s;port=%s;dbname=%s;charset=%s',
            $config['host'],
            $config['port'],
            $config['base'],
            $config['charset']
        );
    }
}
